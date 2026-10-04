"""Code each reply's stance on a -5..+5 scale (-5 strongly favors option A, +5 strongly favors B).

usage: python stance.py --lines 0 1 2 [--file single_reply.jsonl] [--judge openai/gpt-6.1-sol] [--repeats 1]
"""
import argparse, json, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from judge import RUNS, NO_TEMPERATURE, api_key, options_for

OUT = RUNS / "stances.jsonl"

PROMPT = """You are coding which option a reply to a moral dilemma favors.

DILEMMA:
{dilemma}

OPTION A: {option_a}
OPTION B: {option_b}

REPLY:
{reply}

Rate the reply's position on a scale from -5 to +5:
  -5 = strongly favors A (recommends A clearly and without reservation)
  -2 = leans toward A (favors A, or a middle path that is mostly A)
   0 = neither (a balanced middle path, or no recommendation between A and B)
  +2 = leans toward B (favors B, or a middle path that is mostly B)
  +5 = strongly favors B (recommends B clearly and without reservation)
Use any integer in between. Judge what the reply recommends doing, not how sympathetic it sounds
to each side.

Return JSON: {{"stance": <integer from -5 to 5>, "rationale": "<one sentence>"}}"""

SCHEMA = {"type": "json_schema", "json_schema": {"name": "stance", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["stance", "rationale"],
    "properties": {"stance": {"type": "integer", "minimum": -5, "maximum": 5}, "rationale": {"type": "string"}}}}}


def code(model, prompt, key):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "response_format": SCHEMA}
    if not model.startswith(NO_TEMPERATURE):
        body["temperature"] = 0
    resp = {}
    for attempt in range(6):
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                              headers={"Authorization": f"Bearer {key}"}, json=body, timeout=300)
            r.raise_for_status()
            resp = r.json()
        except requests.RequestException as e:  # network blip or server error: back off and retry
            if attempt == 5 or getattr(getattr(e, "response", None), "status_code", None) == 402:
                raise
            time.sleep(min(60, 2 * 2 ** attempt))
            continue
        try:
            out = json.loads(resp["choices"][0]["message"]["content"])
            if isinstance(out.get("stance"), int) and -5 <= out["stance"] <= 5:
                return resp, out, attempt
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return resp, None, attempt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="single_reply.jsonl")
    ap.add_argument("--lines", type=int, nargs="+", required=True)
    ap.add_argument("--judge", default="openai/gpt-6.1-sol")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--out", default=OUT.name, help="output file in runs/ (separate files avoid concurrent appends)")
    args = ap.parse_args()
    lines = (RUNS / args.file).read_text().splitlines()
    key = api_key()

    jobs = []
    for ln in args.lines:
        rec = json.loads(lines[ln])
        opts = options_for(rec["dilemma"])
        prompt = PROMPT.format(dilemma=rec["dilemma"], reply=rec["reply"], **opts)
        jobs += [(ln, opts, prompt, k) for k in range(args.repeats)]

    # Resume: skip (reply, judge, repeat) that already has a valid code; write each code as it returns.
    out_path = RUNS / args.out
    done = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            s = json.loads(line)
            if s.get("valid"):
                done.add((s["reply_ref"], s["judge"], s["repeat"]))
    todo = [j for j in jobs if (f"{args.file}:{j[0]}", args.judge, j[3]) not in done]
    print(f"{len(jobs)} codes, {len(jobs) - len(todo)} already done, {len(todo)} to run", flush=True)
    lock = threading.Lock()
    with ThreadPoolExecutor(12) as ex, out_path.open("a") as f:
        futs = {ex.submit(code, args.judge, j[2], key): j for j in todo}
        for fut in as_completed(futs):
            ln, opts, _, k = futs[fut]
            resp, out, retries = fut.result()
            with lock:
                f.write(json.dumps({
                    "time": time.time(), "reply_ref": f"{args.file}:{ln}", "judge": args.judge, "repeat": k,
                    "model": resp.get("model"), "usage": resp.get("usage"), "retries": retries, "valid": out is not None,
                    "stance": out and out["stance"], "rationale": out and out["rationale"], "options": opts,
                }) + "\n")
                f.flush()
            print(f"{ln:3} {out['stance'] if out else '-':>3}  {out['rationale'] if out else 'INVALID'}", flush=True)


if __name__ == "__main__":
    main()
