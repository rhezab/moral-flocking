"""Export the raw records behind the four natural runs (forum + control) to data/natural/<dilemma>/.

For each dilemma this writes:
  discussion.jsonl  every private answer and public post (round 0 included), as logged by discussion.py
  stances.jsonl     stance codes (-5 = option A, +5 = option B; 3 repeats per reply)
  judgments.jsonl   MoReBench rubric judgments (neutral and/or theory rubrics)

Records keep their original "reply_ref"/"_ref" key (e.g. "discussion.jsonl:123"), so stances and
judgments join to discussion records on ref. No API calls.

usage: python export_natural.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
OUT = HERE / "data" / "natural"
NATURAL = [  # (slug, data file, run_id)
    ("covert-medication", "discussion.jsonl", "20261004-153211"),
    ("pandemic-research", "discussion.jsonl", "20261004-152528"),
    ("county-services", "discussion.jsonl", "20261004-153710"),
    ("community-bank", "discussion_plant.jsonl", "20261004-154443"),
]


def read(name):
    return [json.loads(line) for line in (RUNS / name).read_text().splitlines()]


def main():
    files = {f.name: read(f.name) for f in RUNS.glob("discussion*.jsonl")}
    stances = [s for f in RUNS.glob("stances*.jsonl") for s in read(f.name)]
    judgments = [j for f in RUNS.glob("judgments*.jsonl") for j in read(f.name)]
    for slug, fname, run in NATURAL:
        recs = {f"{fname}:{i}": r for i, r in enumerate(files[fname])
                if r["run_id"] == run and r["group"] in ("control", "forum")}
        r0run = next(iter(recs.values()))["round0_from"]
        for name, rows in files.items():  # round 0: the one shared answer per model (sample 0) the run reused
            for i, r in enumerate(rows):
                if r["run_id"] == r0run and r["condition"] == "round0" and r["agent"] == "sample 0":
                    recs[f"{name}:{i}"] = r
        d = OUT / slug
        d.mkdir(parents=True, exist_ok=True)
        rows = sorted(({"ref": ref, **r} for ref, r in recs.items()), key=lambda r: (r["condition"] != "round0", r["group"], r["round"], r["kind"], r["agent"]))
        for name, out in (("discussion", rows),
                          ("stances", [s for s in stances if s["reply_ref"] in recs]),
                          ("judgments", [j for j in judgments if j["reply_ref"] in recs])):
            (d / f"{name}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out))
            print(f"{slug:18} {name:10} {len(out):5}")


if __name__ == "__main__":
    main()
