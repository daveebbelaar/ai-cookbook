# Data pipeline documentation

Our data pipeline is the bridge between raw customer events and the dashboards / billing aggregates the customer actually sees.

## Overview

```
Customer events (Kafka)
    │
    ├─► Stream processor (Flink) ─► hot dashboards (sub-minute)
    │
    └─► Hourly micro-batch (Airflow) ─► warehouse (BigQuery)
                                            │
                                            └─► Nightly batch ETL (Airflow)
                                                    │
                                                    └─► aggregates table (Postgres)
```

The hot path matters for the dashboard. The cold path matters for billing and trend reports.

## Schedules

We run three categories of scheduled jobs. All times are UTC.

### Stream processor (Flink)

Continuous. Runs 24/7. SLO: events visible in dashboards within 90 seconds of being emitted.

### Hourly micro-batch (Airflow)

Runs at the top of every hour. Pulls the previous hour's window from Kafka into BigQuery. Typical runtime: 4-6 minutes.

### Nightly batch ETL (Airflow)

Runs at **02:00 UTC**, processes all data from the previous calendar day in BigQuery, writes aggregates to Postgres for the billing service to consume. Typical runtime varies by load:

- Median: 6 minutes
- 95th percentile: 9 minutes 12 seconds
- Worst observed: 9 minutes 50 seconds (during a customer XYZ backfill — see `03-incident-2024-q3.md`)

There is also a **European batch ETL** that runs at **03:30 UTC** for region-specific aggregations. This is what landed us in incident 2024-Q3-007.

## Deploy schedule

The nightly heavy-deploy job — which runs migrations, rebuilds vector indexes, and restarts services — kicks off at **03:47 UTC**. The 5-minute buffer past the European ETL's worst-case finish time is intentional and was set after incident 2024-Q3-007. Do not change this schedule without reading that report and coordinating with the platform team.

The exact rationale: the European batch ETL is scheduled at 03:30 UTC and has a worst-observed runtime of 9m50s, putting its absolute latest finish at 03:39:50. The deploy at 03:47 leaves ~7 minutes of buffer in the worst case we've seen, which we round to "5 minutes safely past worst case" in shorthand. Anyone changing the deploy time needs to re-derive this from current ETL metrics.

## Backfills

We backfill into BigQuery, not Postgres. Customer-initiated backfills are queued and processed in FIFO order, max two concurrent. The queue is visible at `admin.nimbuslabs.internal/etl/backfills`.

A backfill exceeding 4 hours of runtime is a flag — usually means we're processing a customer who was missing data for more than a month, or there's an issue with the partition pruning. Page the on-call.

## Failures

If the nightly batch ETL fails:

1. The failure alerts fire at 02:30 UTC (so we have a chance to fix things before the deploy at 03:47)
2. Re-run via `airflow trigger_dag --conf '{"backfill_date": "..."}' nightly_etl`
3. If that fails too, do *not* run the nightly deploy — block it manually via `kubectl scale --replicas=0 deployment/argocd-deploy-trigger`

## SLOs

| Pipeline | SLO | Penalty |
|---|---|---|
| Stream → dashboard | 95% of events visible in 90s | dashboard staleness alert |
| Hourly batch | 99% complete by H+15min | data freshness alert |
| Nightly batch | 99% complete by 03:00 UTC | dashboard yesterday-data is stale |
| Deploy | success rate > 99% per week | rollout policy review |
