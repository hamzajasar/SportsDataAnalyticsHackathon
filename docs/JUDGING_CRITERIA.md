# Judging criteria

**30 points total — six criteria, scored 1–5 each.**
Sports Analytics Hackathon · IUS · 11–13 November 2026

## Jury (3)
1. **Sports-data professional** – will probe methodology, data handling, validation
2. **Coach or club representative** – wants actionable insight they could use on Monday
3. **Expert in youth work and social impact** – wants to know who benefits and who is included

Every part of the pitch should land for all three: rigorous enough for #1, practical for #2, socially meaningful for #3.

## Criteria and how we hit each one

| # | Criterion | What the jury likely looks for | How we show it |
|---|---|---|---|
| 1 | **Relevance of the sports problem** | A real problem that real people in sport have | Name the user (coach, youth club, player, federation) and the decision we help with. One-sentence pitch. |
| 2 | **Data quality and analytical soundness** | Data understood and cleaned; methods appropriate; results validated, not overclaimed | `make profile` output, cleaning steps, baseline vs model, time-aware split, stated limitations. App **Methodology** page. |
| 3 | **Technical execution** | It works, it's well-built, it's not just a notebook | Live full-stack app (React + FastAPI + DB), clean code, CI, deployed URL. |
| 4 | **Innovation and creativity** | A fresh angle, a non-obvious insight, a compelling visualisation | One "wow" insight or visual (map, pitch, timeline, what-if simulator). |
| 5 | **Feasibility, impact and inclusion** | Could this actually be used? Who benefits? Does it widen access (youth, girls/women, low-resource clubs, disability)? | Concrete adoption path, low cost to run, who is included and how; impact in numbers where possible. |
| 6 | **Presentation quality** | Clear story, good demo, within time | Problem → data → insight → demo → impact. Rehearsed; backup screenshots/recording. |

## Implications for picking a topic
- Prefer topics where **#1 and #5 are naturally strong** (clear user + social angle) — these are hard to fake later.
- #2 depends on the dataset: check with `make profile` before committing.
- #3, #6 are largely under our control (the repo is ready for #3).
- Plain language: the coach and youth-work jurors are not data scientists — explain metrics in sports terms.
