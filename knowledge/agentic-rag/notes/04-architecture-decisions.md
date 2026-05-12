# Architecture decision records

Lightweight ADRs. Every entry: context, decision, alternatives considered, consequences. Keep them short.

## ADR-014: migrate vector store from Pinecone to LanceDB

**Date**: 2024-04-22
**Status**: Accepted

### Context

We were paying ~$1,800/month for a Pinecone p1.x1 pod that held our internal-search embeddings. The dataset was small enough (3.2M vectors at 1024-dim) that the recurring cost felt out of proportion to the value. Two issues drove the migration:

1. Cost. $21K/year for what amounts to a fancy lookup table.
2. We needed snapshot-able vector indexes for our customer-deployed product, and Pinecone doesn't ship that way.

### Decision

Move all vector workloads to LanceDB, embedded in the same process as the consuming service. For the customer-deployed product, ship a `.lance` directory alongside the docker image.

### Alternatives considered

- **Stay on Pinecone**: rejected on cost.
- **pgvector on our existing Postgres**: rejected because we didn't want to grow the Postgres footprint and pgvector's recall on cosine-similarity at our dataset size was 4-5% lower than LanceDB in our offline benchmarks.
- **Qdrant self-hosted**: real option, but we'd be running another stateful service. LanceDB's "embedded library" model meant zero new infra.

### Consequences

- $21K/year saved. Migration paid for itself in the first month.
- We gave up Pinecone's metadata filter performance — LanceDB filters are slightly slower at 95p, but well within our latency budget.
- Easier customer deployments: the vector index is a directory you can `tar.gz`.

## ADR-018: Postgres connection pool ceiling at 200

**Date**: 2024-06-10
**Status**: Accepted

### Context

We were periodically seeing `FATAL: too many connections` errors from RDS. Our Postgres instance is configured with `max_connections=400`, of which 50 are reserved for superuser/admin work, leaving 350 for application traffic. With seven services running 3-12 replicas each, we were creeping close to the ceiling under burst load.

### Decision

Each service has a documented per-replica pool size, and the **total ceiling across all services is 200 connections** (giving us 150 connections of headroom for spikes, admin sessions, and emergency manual queries).

Per-service quotas:

- `core/api`: 6 connections × up to 12 replicas = 72
- `core/billing`: 12 connections × up to 4 replicas = 48 — billing runs heavier transactions, hence the larger per-replica pool
- `core/auth`: 4 connections × up to 8 replicas = 32
- `etl-worker`: 8 connections × up to 4 replicas = 32
- Everything else: 16 reserved

### Alternatives considered

- **Bump `max_connections` on RDS**: declined — connections are not free; each one allocates ~10MB of work_mem-adjacent memory. We'd rather right-size pools than throw connections at the problem.
- **PgBouncer in front of RDS**: deferred. We'll revisit when we cross 4× our current traffic.

### Consequences

- We have a headroom budget. New services need to formally request a slice.
- Connection exhaustion alerts now fire at 75% of the per-service quota, not at the global ceiling.

## ADR-021: standardize on FastAPI for new services

**Date**: 2024-09-30
**Status**: Accepted

Inherited services use a mix of Flask, FastAPI, and (one) Bottle app. New services use FastAPI exclusively. Migrate at convenience, not by force.
