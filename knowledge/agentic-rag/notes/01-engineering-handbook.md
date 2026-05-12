# Engineering handbook

This is the canonical reference for how we build and ship software at Nimbus Labs. Read it on your first week, skim it when you're stuck, and update it when something is wrong.

## Stack

- **Language**: Python 3.12+ for backend, TypeScript for frontend
- **Web framework**: FastAPI for services, Next.js 15 for the dashboard
- **Database**: PostgreSQL 16 (managed on Neon for non-prod, RDS for prod)
- **Queue**: Redis 7 with RQ for jobs that finish in under a minute, Temporal for everything else
- **Object storage**: S3 with KMS-managed keys
- **Vector storage**: LanceDB (we migrated from Pinecone in Q2 — see `04-architecture-decisions.md`)
- **Observability**: OpenTelemetry → Grafana Tempo + Loki, dashboards in Grafana Cloud
- **CI/CD**: GitHub Actions, deploys via ArgoCD into our k8s cluster

## Code style

We use `ruff` with the default rule set plus `I` (isort) and `B` (bugbear). Format with `ruff format`. Type-check with `mypy --strict` for any module under `src/nimbuslabs/core`. Outside of `core`, types are encouraged but not enforced — pragmatism over purity.

Functions over classes wherever possible. We have a soft limit of 50 lines per function. If you're approaching it, the function is doing too much.

## Code review

- One reviewer required, two for anything touching `core/billing` or `core/auth`
- Reviews are due within one business day. If you're going to be slower, post in `#eng-async`.
- "LGTM with nits" is fine. "Approve with blocking comments" is not — either approve or request changes.

## Branching

`main` is always deployable. Feature branches off `main`, named `<your-initials>/<topic>`. Squash-merge into `main`. We do not use long-lived release branches.

## Deploys

Deploys are continuous: every merge to `main` rolls out to production within ~10 minutes via ArgoCD. The exception is the **nightly heavy-deploy job**, which runs a full database migration window and a vector-index rebuild. The schedule and rationale are documented in `07-data-pipeline-docs.md`.

## On-call

We rotate weekly, Mon 09:00 UTC to the following Mon 09:00 UTC. The on-call runbook lives in `02-billing-runbook.md` for billing-specific issues; for everything else see the incident response process in `03-incident-2024-q3.md`.
