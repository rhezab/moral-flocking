"""Extract the data behind the natural-run report (control + forum, simultaneous posting) into
reports/natural.json: per-agent stances by round, post stances, rubric scores, mentions and
side-to-side influence traces. No API calls.

usage: python reports/natural_data.py
"""
import collections, json, re, statistics

import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"
ITEMS = json.loads((HERE.parent / "items.json").read_text())
JUDGE = "openai/gpt-6.1-sol"
THEORIES = ["neutral", "Act Utilitarianism", "Kantian Deontology", "Aristotelian Virtue Ethics",
            "Scanlonian Contractualism", "Gauthierian Contractarianism"]
NATURAL = [  # (name, data file, run_id)
    ("Pandemic research", "discussion.jsonl", "20261004-152528"),
    ("Covert medication", "discussion.jsonl", "20261004-153211"),
    ("County services", "discussion.jsonl", "20261004-153710"),
    ("Community bank", "discussion_plant.jsonl", "20261004-154443"),
]
MENTION = re.compile(r"\bAgents? (\d+)((?:(?:, and |, | and | & )\d+)*)")


def load():
    recs = {}
    for f in RUNS.glob("discussion*.jsonl"):
        if "dryrun" in f.name:
            continue
        for i, line in enumerate(f.read_text().splitlines()):
            r = json.loads(line)
            r["_ref"] = f"{f.name}:{i}"
            recs[r["_ref"]] = r
    stance = collections.defaultdict(list)
    for f in RUNS.glob("stances*.jsonl"):
        for line in f.read_text().splitlines():
            s = json.loads(line)
            if s.get("valid"):
                stance[s["reply_ref"]].append(s["stance"])
    scores = collections.defaultdict(dict)  # ref -> rubric -> % of max
    crit = {}  # (ref, rubric) -> list of applies
    for f in RUNS.glob("judgments*.jsonl"):
        for line in f.read_text().splitlines():
            j = json.loads(line)
            if j.get("valid") and j.get("judge") == JUDGE:
                w = j["weights"]
                scores[j["reply_ref"]][j.get("rubric", "neutral")] = round(100 * sum(a * x for a, x in zip(j["applies"], w)) / sum(x for x in w if x > 0), 1)
                crit[(j["reply_ref"], j.get("rubric", "neutral"))] = (j["applies"], j["criteria"])
    return recs, stance, scores, crit



def mca(rows):
    """Multiple correspondence analysis of 0/1 criterion vectors (one row per response).
    Returns row principal coordinates (dims 1-2) and Benzecri-corrected % of inertia."""
    X = np.asarray(rows, float)
    X = X[:, X.std(0) > 0]  # keep criteria that vary
    q = X.shape[1]
    Z = np.hstack([X, 1 - X])
    P = Z / Z.sum()
    r, c = P.sum(1), P.sum(0)
    S = (P - np.outer(r, c)) / np.sqrt(np.outer(r, c))
    U, sv, _ = np.linalg.svd(S, full_matrices=False)
    F = (U * sv) / np.sqrt(r)[:, None]
    lam = sv ** 2
    adj = np.where(lam > 1 / q, ((q / (q - 1)) * (lam - 1 / q)) ** 2, 0)
    return F[:, :2], (100 * adj[:2] / adj.sum()).round(1).tolist(), q


def pca(rows):
    """PCA of theory-score vectors (% of max, same units, so not standardized)."""
    X = np.asarray(rows, float)
    Xc = X - X.mean(0)
    U, sv, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = sv ** 2
    return Xc @ Vt[:2].T, (100 * var[:2] / var.sum()).round(1).tolist(), Vt[:2].T


def orient(coords, stance):
    """Flip each axis so that larger x/y go with option B where they correlate with stance."""
    st = np.asarray(stance, float)
    for j in range(coords.shape[1]):
        if np.corrcoef(coords[:, j], st)[0, 1] < 0:
            coords[:, j] *= -1
    return coords


def short_name(m):
    return m.split("/")[-1]


def mentions(text):
    return [f"Agent {n}" for m in MENTION.finditer(text) for n in [m.group(1), *re.findall(r"\d+", m.group(2))]]


def main():
    recs, stance, scores, crit = load()
    st = lambda ref: round(statistics.mean(stance[ref]), 2) if stance.get(ref) else None
    out = []
    for name, fname, run in NATURAL:
        R = [r for r in recs.values() if r["run_id"] == run and r["_ref"].startswith(fname + ":")]
        dilemma = R[0]["dilemma"]
        opts = next(v for k, v in ITEMS.items() if dilemma.startswith(k))
        r0run = R[0]["round0_from"]
        r0 = {r["model_requested"]: r for r in recs.values()
              if r["run_id"] == r0run and r["condition"] == "round0" and r["agent"] == "sample 0"}
        rubrics = [t for t in THEORIES if any(t in scores[r["_ref"]] for r in R if r["kind"] == "private")]
        d = {"name": name, "run": run, "options": opts, "rubrics": rubrics, "dilemma": R[0].get("dilemma_shown") or dilemma,
             "conds": {}, "posts": [], "mentions": {}, "sides": []}
        for cond in ("control", "forum"):
            agents = {}
            for r in R:
                if r["group"] == cond and r["kind"] == "private":
                    a = agents.setdefault(r["agent"], {"agent": r["agent"], "model": r["model_requested"], "refs": {}})
                    a["refs"][r["round"]] = r["_ref"]
            for a in agents.values():
                a["refs"][0] = r0[a["model"]]["_ref"]
                a["st"] = [st(a["refs"].get(k)) for k in range(4)]
                a["sc"] = [{t: scores[a["refs"][k]].get(t) for t in rubrics} if a["refs"].get(k) else {} for k in range(4)]
            d["conds"][cond] = sorted(agents.values(), key=lambda a: a["model"])
        posts = [r for r in R if r["group"] == "forum" and r["kind"] == "public"]
        d["posts"] = [{"round": r["round"], "model": r["model_requested"], "st": st(r["_ref"]), "order": r.get("post_order")} for r in posts]

        # Mentions in the forum (posts + private answers): who names whom; self-mentions counted separately.
        fa = {a["agent"]: a for a in d["conds"]["forum"]}
        named, selfm, total = collections.Counter(), 0, 0
        for r in R:
            if r["group"] != "forum":
                continue
            for lab in mentions(r["reply"]):
                if lab not in fa:
                    continue
                total += 1
                if lab == r["agent"]:
                    selfm += 1
                else:
                    named[fa[lab]["model"]] += 1
        d["mentions"] = {"named": dict(named), "self": selfm, "total": total}

        # Side-to-side traces per transition k-1 -> k (forum): mentions in the private answer at k, and
        # newly met rubric criteria (neutral, else all theory rubrics) shared with peers who met them at k-1.
        def side(v):
            return None if v is None else "A" if v < 0 else "B" if v > 0 else "0"
        crit_rubrics = ["neutral"] if "neutral" in rubrics else rubrics
        for k in (1, 2, 3):
            rows = collections.defaultdict(lambda: {"n": 0, "delta": [], "crossed": 0, "cites": collections.Counter(),
                                                    "shared": collections.Counter(), "avail": collections.Counter()})
            for a in fa.values():
                s0, s1 = a["st"][k - 1], a["st"][k]
                row = rows[side(s0)]
                row["n"] += 1
                if s0 is not None and s1 is not None:
                    row["delta"].append(s1 - s0)
                    if side(s0) in "AB" and side(s1) in "AB" and side(s0) != side(s1):
                        row["crossed"] += 1
                peers = [p for p in fa.values() if p is not a]
                for p in peers:
                    row["avail"][side(p["st"][k - 1])] += 1
                ref = a["refs"].get(k)
                for lab in mentions(recs[ref]["reply"]) if ref else []:
                    p = fa.get(lab)
                    if p and p is not a:
                        row["cites"][side(p["st"][k - 1])] += 1
                for rub in crit_rubrics:
                    now, prev = crit.get((a["refs"].get(k), rub)), crit.get((a["refs"].get(k - 1), rub))
                    if not now or not prev:
                        continue
                    for i, (x, y) in enumerate(zip(now[0], prev[0])):
                        if x and not y:
                            for p in peers:
                                pc = crit.get((p["refs"].get(k - 1), rub))
                                if pc and pc[0][i]:
                                    row["shared"][side(p["st"][k - 1])] += 1
            for sd, row in rows.items():
                d["sides"].append({"k": k, "side": sd, "n": row["n"],
                                   "delta": round(statistics.mean(row["delta"]), 2) if row["delta"] else None,
                                   "crossed": row["crossed"], "cites": dict(row["cites"]), "shared": dict(row["shared"]),
                                   "avail": dict(row["avail"])})
        # Citations: for each forum agent and round k, the peers it names in its round-k private answer and
        # in its phase-k public post, with the sentence (agent labels replaced by model names).
        lab2model = {a["agent"]: a["model"] for a in d["conds"]["forum"]}
        post_of = {(r["agent"], r["round"]): r for r in R if r["group"] == "forum" and r["kind"] == "public"}

        def named(text, me):
            out = []
            for sen in re.split(r"(?<=[.!?])\s+", text):
                labs = [l for l in dict.fromkeys(mentions(sen)) if l in lab2model and l != me]
                if not labs:
                    continue
                quote = MENTION.sub(lambda m: ", ".join(short_name(lab2model.get(f"Agent {n}", f"Agent {n}"))
                                                         for n in [m.group(1), *re.findall(r"\d+", m.group(2))]), sen.strip())
                out += [{"to": lab2model[l], "quote": quote[:320]} for l in labs]
            return out
        for a in d["conds"]["forum"]:
            a["cites"] = [None] + [
                [dict(c, where="private") for c in named(recs[a["refs"][k]]["reply"], a["agent"])] +
                [dict(c, where="post") for c in named(post_of[(a["agent"], k)]["reply"], a["agent"])] if (a["agent"], k) in post_of else []
                for k in (1, 2, 3)]

        # Maps: one MCA (rubric criteria) and one PCA (theory scores) per dilemma, fitted on every private
        # answer in both conditions (round 0 shared), so positions are comparable across rounds and conditions.
        basis = ["neutral"] if "neutral" in rubrics else rubrics
        items = {}  # ref -> (criteria vector, theory vector, stance)
        theories = [t for t in rubrics if t != "neutral"]
        for c in d["conds"].values():
            for a in c:
                for k, ref in a["refs"].items():
                    if ref in items:
                        continue
                    vec = [x for rub in basis for x in (crit.get((ref, rub)) or ([None], []))[0]]
                    th = [scores[ref].get(t) for t in theories]
                    if None not in vec and st(ref) is not None:
                        items[ref] = (vec, th, st(ref))
        refs = list(items)
        F, mpct, q = mca([items[r][0] for r in refs])
        F = orient(F, [items[r][2] for r in refs])
        mpos = {r: F[i].round(4).tolist() for i, r in enumerate(refs)}
        d["mca"] = {"pct": mpct, "basis": "neutral rubric" if basis == ["neutral"] else "all theory rubrics", "criteria": q, "n": len(refs)}
        ppos = {}
        if len(theories) >= 3:
            prefs = [r for r in refs if None not in items[r][1]]
            G, ppct, loads = pca([items[r][1] for r in prefs])
            G = orient(G, [items[r][2] for r in prefs])
            sign = np.sign([np.corrcoef(G[:, j], (np.asarray([items[r][1] for r in prefs]) - np.mean([items[r][1] for r in prefs], 0)) @ loads[:, j])[0, 1] for j in range(2)])
            ppos = {r: G[i].round(3).tolist() for i, r in enumerate(prefs)}
            d["pca"] = {"pct": ppct, "load": [[t, round(float(loads[i, 0] * sign[0]), 3), round(float(loads[i, 1] * sign[1]), 3)] for i, t in enumerate(theories)], "n": len(prefs)}
        for c in d["conds"].values():
            for a in c:
                a["mca"] = [mpos.get(a["refs"].get(k)) for k in range(4)]
                a["pca"] = [ppos.get(a["refs"].get(k)) for k in range(4)] if ppos else None
        for c in d["conds"].values():
            for a in c:
                del a["refs"]
        out.append(d)
    (HERE / "natural.json").write_text(json.dumps(out, indent=1))
    for d in out:
        f = d["conds"]["forum"]
        print(f"{d['name']:20} forum R0 {statistics.mean(a['st'][0] for a in f):+.2f} -> R3 {statistics.mean(a['st'][3] for a in f if a['st'][3] is not None):+.2f}"
              f" | rubrics {len(d['rubrics'])} | mentions {d['mentions']['total']} (self {d['mentions']['self']})")


if __name__ == "__main__":
    main()
