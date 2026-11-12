# Hackathon day playbook

## Hour 0 – setup (15 min)
1. Everyone: clone, `make setup`, `make dev` → app on http://localhost:5173, API docs on http://localhost:8000/docs
2. Put the provided datasets in `data/raw/` (share files via drive, **not git**)
3. `make profile` → read `data/processed/_profile.md`; open the **Data** page in the app
4. Put the brief + judging criteria in `docs/`

## Hour 0–1 – choose the topic
Score each topic 1–5 against the **actual judging criteria** (see [JUDGING_CRITERIA.md](JUDGING_CRITERIA.md)):

| Criterion | Questions to ask about the topic | Topic A | Topic B | Topic C |
|---|---|---|---|---|
| Relevance of the sports problem | Is there a real user (coach, club, youth org) with a real decision? | | | |
| Data quality & analytical soundness | Enough rows? Missing values? Clean joins? (`make profile`) | | | |
| Technical execution | Can we build a working app around it in the time? | | | |
| Innovation & creativity | Is there a non-obvious insight or a standout visual? | | | |
| Feasibility, impact & inclusion | Who benefits? Does it help youth / underrepresented groups / small clubs? | | | |
| Presentation quality | Can we explain it to a coach in one sentence? | | | |
| **Total** | | | | |

The jury is a **sports-data pro, a coach/club rep and a youth-work/social-impact expert** — pick the topic that can satisfy all three.

Write the **one-sentence pitch** before writing code: _"We help <who> to <decision> by <insight from data>, so that <social impact>."_

## Roles (adjust to team size)
- **Data/ML** – notebooks → move logic into `backend/app/services/`
- **Backend** – endpoints in `backend/app/api/routes/`, `make gen-api` after each change
- **Frontend** – pages in `frontend/src/pages/`, reuse `components/common/*`
- **Story/presentation** – README sections, slides, demo script, screenshots (start early!)

## Rhythm
- Small PRs into `main`; `make check` before pushing
- Sync every ~2h: what works, what's blocked, cut scope if behind
- Freeze features ~2h before the end → polish, fix bugs, rehearse demo
- Keep a fallback: screenshots / recording of the demo in case live demo fails

## Presentation (~5 min) — each part maps to a criterion
1. **Problem + who cares** (30s) → _Relevance_
2. **Data**: what, how much, how cleaned, limitations (30s) → _Data quality & soundness_
3. **Approach**: method + why; baseline vs our result, in plain sports language (1 min) → _Soundness_, _Innovation_
4. **Live demo** (2 min) → _Technical execution_, _Innovation_
5. **Impact & inclusion**: who uses it, who benefits, cost to adopt, next steps (1 min) → _Feasibility, impact & inclusion_
6. Rehearse twice, keep to time, have a backup recording → _Presentation quality_
