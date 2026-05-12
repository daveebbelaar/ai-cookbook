# Onboarding guide

Welcome. This is what to do in your first two weeks. Don't try to do everything at once.

## Day 1

1. Get your laptop. We use M-series MacBooks; a 14" Pro is plenty unless you're doing GPU work.
2. Set up your dev environment: `git clone`, `uv sync`, `make bootstrap`. The bootstrap script writes `.env.local` from `.env.example` and pulls down the dev seed database.
3. Slack channels you should be in: `#eng`, `#eng-async`, `#alerts-prod`, `#random`. You'll be added automatically; if you're not, ping anyone.
4. Pair with whoever onboarded you for an hour on the codebase tour.

## Week 1

- **Ship a real PR.** Pick something off the `good-first-issue` label and put up a PR by Friday. The point is to feel the code review process, not to do something heroic.
- **Read the wiki.** Specifically: `01-engineering-handbook.md`, `02-billing-runbook.md`, and at least one ADR from `04-architecture-decisions.md`. The handbook is short; the runbook will save you on your first on-call.
- **Get on-call shadow rotation.** You'll be paired with the primary on-call for one week before you take a primary shift yourself.

## Week 2

- Pick a project. We do six-week cycles; whoever you're working with will fit you in.
- Set up your `~/.zshrc` with our shared aliases. Optional but the team uses them: `make dotfiles` clones our shared dotfiles repo into a sibling directory.
- Do your first deploy. The deploy schedule is documented in `07-data-pipeline-docs.md` — if your change is going to run as part of the nightly heavy-deploy window, the on-call will tell you.

## Tools you'll need accounts for

| Tool | Who provisions | When |
|---|---|---|
| GitHub org | Marc | Day 0 |
| 1Password vault | Priya | Day 0 |
| AWS console | Marc | Day 1 |
| Stripe (read-only) | Priya | Week 1, only if you're touching billing |
| Sentry | self-serve via Google SSO | Day 1 |
| Grafana | self-serve via Google SSO | Day 1 |
| PagerDuty | Lukas | Week 1 |

## Cultural notes

- We default to async. Long Slack threads should become docs in this wiki.
- We value clear writing. Your PR descriptions are part of how we evaluate you.
- We do not do hero work. If a project requires weekend work to ship on time, the project is wrong, not the person.
- We say no to unscoped meetings. If there's no agenda, there's no meeting.

## Useful Slack reactions

- `:done:` — task is complete
- `:eyes:` — I'm looking at this
- `:bookmark:` — I'll come back to this; please don't unfurl
- `:rocket:` — ship it

## Your buddy

You'll be assigned a buddy for the first month. They are your "no question is dumb" person. Use them.
