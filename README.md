# An exploration of the "moral flocking" hypothesis

**Do AI groups tend towards moral consensus?**

By [Rheza Budiono](https://rhezab.github.io) ([@rhezab](https://github.com/rhezab)) & [Jacob Shkrob](https://shkroby.github.io) ([@shkroby](https://github.com/shkroby)) for the [AI Swarm Dynamics Hackathon](https://swarmchasing.com).

**Write-up: [Moral Flocking (Google Doc)](https://docs.google.com/document/d/1YksK94lv16rP_Wk0vDqtKcQo9EURY3ARCyXUiygQuLA/edit?tab=t.0#heading=h.4wci1qdmmzj2)** · [Transcript explorer](https://claude.ai/artifact/D3zHr3nZ3ThTSF2cThwMbp) · [Static report](https://claude.ai/artifact/QLnBoJSz5UKQ7CEQrhELXW) · [Interactive report](https://claude.ai/artifact/NFbrzMjpbywHQEZUr6AQQ6)

> **AI use statement:** The Google Doc write-up is human-written by the authors. Most other write-ups in this repo — this README, the report pages and transcript explorer (`reports/*.html`), `reports/transcript_notes.md`, `forum-insights.md`, `discussion-design.md` and `morebench-threads.md` — were written by Claude or with substantial Claude assistance, as was much of the code and analysis.

> **Status:** work in progress, built for a hackathon. Results come from single runs per condition and an LLM judge; treat them as preliminary.

## Summary

The **moral flocking hypothesis**: (LLM assistant) AIs interacting with each other will tend toward swarm-like moral consensus, even when the AIs are different models from different providers.

We took four binary moral dilemmas from [MoReBench](https://morebench.github.io/) and had 12 AIs (different models) discuss each over three rounds of forum discussion. We found that:
- AIs tended toward consensus in the forum condition, but not in the control condition.
- In the "covert medication" dilemma, an initially split room ends in consensus.
- On the same dilemma, Claude Opus switched sides, convinced by other AIs.
- Collective opinion was fairly robust to two steering interventions: over-representation of one side, and planted persuaders.

## Experiment design
- **Models:** 12 models from 6 providers, a higher-end and a lower-end model from each (OpenAI, xAI, Anthropic, DeepSeek, Zhipu, Qwen).
- **Forum:** three rounds of public discussion (posts ≤ 150 words). Posting is simultaneous: in round N, each AI sees only posts from rounds before N.
- **Private opinions:** each AI gives a private opinion before discussion and after each round (≤ 250 words), seen by no other AI.
- **Reasoning:** before every post and private opinion, AIs may reason privately (capped at 500 tokens).
- **Judge:** an LLM judge (gpt-6.1-sol) codes each private opinion for stance (−5 option A … +5 option B, coded three times and averaged) and for which MoReBench rubric criteria it meets (a neutral rubric and/or moral-theory rubrics, depending on the dilemma).
- **Conditions:** *control* (each AI "discusses" only with itself, re-reading its own answers), *forum*, *over-represent* (extra copies of AIs on one side) and *planted* (persuaders instructed to push one side).

Prompts are in the Google Doc appendix and in `discussion.py`, `stance.py` and `judge.py`.

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
