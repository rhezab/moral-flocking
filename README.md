# Swarmchasing: do language models flock?

Opinion cascades and flocking in moral reasoning among LLM collectives (hackathon submission).

**Authors:** [@rhezab](https://github.com/rhezab) and Jacob Shkrob

> **Disclaimer:** work in progress, built for a hackathon with substantial AI assistance (code, analysis and write-up). Results come from single runs per condition and an LLM stance coder/judge; treat them as preliminary.

Twelve models (two per lab from Anthropic, OpenAI, xAI, Alibaba, DeepSeek, Zhipu) answer a MoReBench moral dilemma alone, then for three rounds either discuss it in a shared forum (simultaneous, anonymous "Agent N" posts) or reflect alone (control). Private answers are stance-coded (-5 option A … +5 option B) and judged against MoReBench rubrics. Follow-ups add planted persuaders (Claude Sonnet 5.5 briefed to argue one side) and skewed starting populations.

**Findings report:** `reports/report.html` · **Interactive explorer:** `reports/dilemmas.html` · **Transcript notes:** `reports/transcript_notes.md`

Key results (one run per condition):
- Discussion makes views converge: stance dispersion falls in the forum and ends lower than in control in all four dilemmas.
- Covert medication: a 6:6 split ends 10:1 for refusing; Claude Opus 5.5 switches after the first round, crediting two peers' arguments. The safeguards stay; the default flips.
- Steering: covert medication is robust to plants and skewed majorities; pandemic research is moderated toward neutral but not reversed.

## Code
- `discussion.py` — runs round 0, control and forum (simultaneous posting, skewed populations `--skew`, planted agents `--plant`)
- `stance.py`, `judge.py` — stance coding and MoReBench rubric judging via OpenRouter
- `run_batch.py` — batch runner (generation → stance → judge, resumable)
- `reports/` — data extraction and report/explorer builders
- `*_viewer/` — local viewers (served by small Python servers)
- `export_natural.py` — exports the raw records for the four natural runs to `data/natural/`

Requires an OpenRouter key in `../.env` as `OPENROUTER_API_KEY=...` (not included).

## Data
Raw records for the four natural runs (forum + control, no plants or skews) are in `data/natural/<dilemma>/`, one folder each for `covert-medication`, `pandemic-research`, `county-services` and `community-bank`:
- `discussion.jsonl` — 120 records: 12 round-0 answers (shared by both conditions), 36 control private answers, 36 forum private answers and 36 forum posts. Each has the full prompt (`messages`), the reply, the provider's hidden reasoning when returned (`reasoning`, capped at 500 tokens; some providers return only a summary), model, round, kind and token usage.
- `stances.jsonl` — stance codes (−5 option A … +5 option B), three repeats per reply.
- `judgments.jsonl` — MoReBench rubric judgments of private answers (neutral rubric; theory rubrics where the dilemma has them).

Join on `ref` (in `discussion.jsonl`) = `reply_ref` (in the other two). Forum agents appear as "Agent N" in the raw text; `agent` and `model_requested` map labels to models. The full raw data for all runs, including plant and skew follow-ups, stays local in `runs/`.
