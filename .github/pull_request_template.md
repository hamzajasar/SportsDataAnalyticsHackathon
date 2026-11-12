<!-- Base branch must be `dev` (never `main`, except the final release PR). -->

## What
<!-- One or two sentences. Screenshot/GIF if UI changed. -->

## Checklist
- [ ] Branch is `feature/<name>`, based on latest `dev` (`make sync` if behind)
- [ ] `make check` passes and CI is green
- [ ] Changed an endpoint/schema → ran `make gen-api`
- [ ] Changed ORM models → added migration (`make migration m="..."`)
- [ ] No data files, secrets or `.env` committed
