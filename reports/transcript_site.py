"""Build reports/transcripts.html: a transcript explorer for the natural runs (control + forum).
Embeds every private answer and public post, with agent labels replaced by model names. No API calls.

usage: python reports/transcript_site.py
"""
import json, re, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from natural_data import NATURAL, ITEMS, MENTION, load, short_name  # noqa: E402
import discussion  # noqa: E402  (prompt templates)


def cot(r, sub):
    """Hidden reasoning returned by the provider (full text or a provider summary), with its token count."""
    tok = ((r.get("usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
    text = (r.get("reasoning") or "").strip()
    return {"r": sub(text) if text else None, "rt": tok}


def main():
    recs, stance, _, _ = load()
    st = lambda ref: round(statistics.mean(stance[ref]), 1) if stance.get(ref) else None
    out = []
    order = ["Covert medication", "Pandemic research", "County services", "Community bank"]
    for name, fname, run in sorted(NATURAL, key=lambda x: order.index(x[0])):
        R = [r for r in recs.values() if r["run_id"] == run and r["_ref"].startswith(fname + ":")]
        dilemma = R[0]["dilemma"]
        opts = next(v for k, v in ITEMS.items() if dilemma.startswith(k))
        r0 = {r["model_requested"]: r for r in recs.values()
              if r["run_id"] == R[0]["round0_from"] and r["condition"] == "round0" and r["agent"] == "sample 0"}
        lab2model = {r["agent"]: r["model_requested"] for r in R if r["group"] == "forum"}

        def sub(text):
            return MENTION.sub(lambda m: ", ".join(
                "[[" + short_name(lab2model[f"Agent {n}"]) + "]]" if f"Agent {n}" in lab2model else f"Agent {n}"
                for n in [m.group(1), *re.findall(r"\d+", m.group(2))]), text)

        models = sorted(r0)
        d = {"name": name, "a": opts["option_a"], "b": opts["option_b"], "dilemma": R[0].get("dilemma_shown") or dilemma,
             "models": [short_name(m) for m in models], "conds": {}}
        for cond in ("control", "forum"):
            label = {r["model_requested"]: r["agent"] for r in R if r["group"] == cond}
            entries = [{"m": models.index(m), "k": 0, "kind": "private", "st": st(r0[m]["_ref"]), "t": r0[m]["reply"], **cot(r0[m], sub)} for m in models]
            for r in R:
                if r["group"] != cond:
                    continue
                entries.append({"m": models.index(r["model_requested"]), "k": r["round"], "kind": r["kind"],
                                "st": st(r["_ref"]), "t": sub(r["reply"]), "o": r.get("post_order"), **cot(r, sub)})
            entries.sort(key=lambda e: (e["k"], e["kind"] == "private", e.get("o") or 0, e["m"]))
            d["conds"][cond] = {"labels": [label.get(m, "") for m in models], "entries": entries}
        out.append(d)

    prompts = {k: getattr(discussion, k).strip() for k in ("SYS_PRIVATE", "ROUND0", "PRIVATE", "SYS_PUBLIC", "PUBLIC")}
    html = (HERE / "transcript_template.html").read_text()
    html = html.replace("/*DATA*/", json.dumps({"dilemmas": out, "prompts": prompts}, ensure_ascii=False).replace("</", "<\\/"))
    (HERE / "transcripts.html").write_text(html)
    print(f"wrote transcripts.html ({len(html) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
