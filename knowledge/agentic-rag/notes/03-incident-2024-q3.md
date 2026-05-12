# Incident report 2024-Q3-007

**Severity**: SEV-2
**Detected**: 2024-08-14 03:48 UTC
**Resolved**: 2024-08-14 05:12 UTC
**Author**: Priya Patel
**Postmortem owner**: Marc Vermeer

## Summary

A scheduled deploy at 03:42 UTC interrupted an in-flight European batch ETL run, leaving partial writes in the `events_processed` table. Downstream metrics were briefly off by ~3% for two hours until the ETL was re-run and the partial rows were reconciled.

No customer data was lost. The dashboard's "events processed today" widget displayed incorrect numbers between 03:42 and 05:12 UTC.

## Timeline

- **03:30 UTC** — European batch ETL job begins. Expected to finish around 03:42 UTC under normal load. This particular run was 90 seconds slower than usual due to a backfill from Customer XYZ that landed in the same window.
- **03:42 UTC** — Scheduled deploy job kicks off (migrations + service restart). At this time the deploy schedule was hardcoded to 03:42 UTC nightly.
- **03:43 UTC** — Migration takes a brief lock on `events_processed`; the still-running ETL transaction is killed mid-write.
- **03:48 UTC** — Anomaly alert fires on the `events_processed_count_lag` metric.
- **04:03 UTC** — Marc traced the cause to the ETL/deploy collision.
- **04:50 UTC** — ETL reconciliation job runs successfully. Numbers come back into agreement.
- **05:12 UTC** — Resolution confirmed. Incident closed.

## Root cause

The deploy job and the European batch ETL were both scheduled at 03:42 UTC, with no buffer between them. On a normal night the ETL finished before the deploy began (~03:41). On this night the ETL ran long, the deploy ran on time, and the two collided.

## Action items

1. **Stagger the deploy schedule.** [DONE 2024-08-15] We shifted the nightly deploy job to **03:47 UTC**, giving the European batch ETL a 5-minute buffer to finish even on slow nights. Documented in `07-data-pipeline-docs.md`.
2. **Add an ETL lock check** to the deploy script. [DONE 2024-08-22] The deploy script now refuses to run if any ETL transaction is older than 60 seconds.
3. **Alert on long-running ETL transactions.** [DONE 2024-09-02] New Grafana alert if any ETL job runs longer than 12 minutes.

## Lessons

- "It's never collided before" is not an SLO. Schedule things with explicit buffers.
- The deploy script needed defense-in-depth — a schedule change is a soft fix; a hard interlock is the real fix.
- The 5-minute buffer was chosen empirically; the slowest ETL we'd ever observed in production was 9 minutes 50 seconds. 5 extra minutes covers 99.9th percentile worst case.
