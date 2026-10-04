"""Run discussion.py jobs in sequence, then stance-code every new record and judge the new private
responses on all available rubrics. Each named batch writes to its own data files
(runs/discussion_<batch>.jsonl, stances_<batch>.jsonl, judgments_<batch>.jsonl; "natural" uses the
main files), so batches can run side by side without appending to the same file. Stops at the
first failure (e.g. out of credit).

usage: python run_batch.py <batch> [--from N] [--post-only RUN_ID]
  --from N             skip the batch's first N jobs (resume after a failure)
  --post-only RUN_ID   for the first job run, skip generation and only stance-code/judge the records of
                       RUN_ID in the batch file (when generation finished but coding failed)
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
SONNET = "anthropic/claude-sonnet-5.5"
# Round-0 screen runs (3 samples per model) that discussion runs start from.
R0 = {"pandemic": "20261004-145157", "county": "20261004-150925", "env": "20261004-151117",
      "bank": "20261004-151305", "covert": "20261004-151353"}
MATCH = {"pandemic": "Track A is an experimental treatment",
         "covert": "caring for a middle-aged man who was involuntarily committed",
         "county": "director of a county social services agency",
         "bank": "chair of a community bank's loan committee"}
BATCHES = {  # batch -> [(dilemma, extra discussion.py args)]
    "natural": [(d, ["--conditions", "control,forum"]) for d in ("pandemic", "covert", "county")],
    # Three Sonnet plants per forum: both sides where models split, the minority side where they agree.
    "plant": [
        ("bank", ["--conditions", "control,forum", "--plant", f"plant-A={SONNET}:A:3"]),  # bank also needs its natural baseline
        ("covert", ["--conditions", "forum", "--populations", "none",
                    "--plant", f"plant-A={SONNET}:A:3", "--plant", f"plant-B={SONNET}:B:3"]),
        ("county", ["--conditions", "forum", "--populations", "none", "--plant", f"plant-B={SONNET}:B:3"]),
        ("pandemic", ["--conditions", "forum", "--populations", "none",
                      "--plant", f"plant-A={SONNET}:A:3", "--plant", f"plant-B={SONNET}:B:3"]),
    ],
    # 12 natural agents + 12 copies of models firmly on one side (each copy starts from its own round-0
    # sample; off-side samples skipped). Copies' extra round-0 samples live in discussion_skew.jsonl.
    "skew": [
        ("covert", ["--conditions", "control,forum", "--populations", "none",
                    "--round0-from", "20261004-151353,20261004-153906,20261004-154736,20261004-155053",
                    "--skew", "A-skew=claude-opus-5.5:1-6,glm-5.3-flash:1-3,glm-5.3-flash:5-7",
                    "--skew", "B-skew=grok-4.7:1-3,grok-4.7:6,gpt-6.1-sol:1-4,deepseek-v4-pro-0813:1-4"]),
        ("pandemic", ["--conditions", "control,forum", "--populations", "none",
                      "--round0-from", "20261004-145157,20261004-154758,20261004-155108,20261004-155145",
                      "--skew", "A-skew=grok-4.7:1-4,deepseek-v4-pro-0813:1-4,glm-5.3-prime:2,glm-5.3-prime:4-6",
                      "--skew", "B-skew=qwen3.8-max-prime:1-2,qwen3.8-max-prime:5-6,qwen3.8-max-prime:12,glm-5.3-flash:1-5,glm-5.3-flash:7-8"]),
    ],
}


def sh(*args):
    print("$", " ".join(args), flush=True)
    subprocess.run([PY, *args], cwd=HERE, check=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--from", dest="start", type=int, default=0)
    ap.add_argument("--post-only", help="run_id whose records to stance-code/judge instead of generating the first job")
    args = ap.parse_args()
    batch = args.batch
    tag = "" if batch == "natural" else f"_{batch}"
    data, stances, judgments = f"discussion{tag}.jsonl", f"stances{tag}.jsonl", f"judgments{tag}.jsonl"
    path = HERE / "runs" / data
    for j, (dilemma, extra) in enumerate(BATCHES[batch][args.start:]):
        start = len(path.read_text().splitlines()) if path.exists() else 0
        if j == 0 and args.post_only:
            recs = path.read_text().splitlines()
            new = [i for i, l in enumerate(recs) if json.loads(l)["run_id"] == args.post_only]
        else:
            r0 = [] if "--round0-from" in extra else ["--round0-from", R0[dilemma]]  # a job may name its own round-0 runs
            sh("discussion.py", "--match", MATCH[dilemma], *r0, "--out", data, *extra)
            recs = path.read_text().splitlines()
            new = list(range(start, len(recs)))
        private = [i for i in new if json.loads(recs[i])["kind"] == "private"]
        print(f"new lines {start}..{len(recs) - 1} ({len(new)} records, {len(private)} private)", flush=True)
        sh("stance.py", "--file", data, "--out", stances, "--repeats", "3", "--lines", *map(str, new))
        sh("judge.py", "--file", data, "--out", judgments, "--rubrics", "all", "--workers", "48", "--lines", *map(str, private))
    print("batch done", flush=True)


if __name__ == "__main__":
    main()
