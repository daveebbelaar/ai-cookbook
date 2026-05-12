# Billing runbook

This runbook covers operational procedures for the billing service: how it works, what breaks, and how to fix it without paging the founder at 3 AM.

## Architecture

The billing service is a FastAPI app at `services/billing`, backed by:

- **PostgreSQL** for the source of truth (subscriptions, invoices, payment methods)
- **Stripe** for actual payment processing
- **Redis** for idempotency keys (24-hour TTL) and webhook deduplication
- **An RQ worker** that processes Stripe webhooks asynchronously

We never trust the client to tell us what to charge. All amounts are computed server-side from the plan and usage tables.

## Common alarms

### `billing_invoice_generation_lag > 5min`

A scheduled job runs every 5 minutes and creates invoices for subscriptions that just rolled over. Lag means the worker is stuck or the queue is backed up.

1. Check `redis-cli LLEN rq:queue:billing` — anything over 200 is bad
2. Look at active workers: `rq info --url $REDIS_URL`
3. If workers are alive but the queue isn't draining, suspect a poison message — `rq requeue --queue billing` after dropping the offending job

### `stripe_webhook_5xx_rate > 1%`

We're returning errors to Stripe, which means Stripe is going to retry. Most often:

1. Webhook signing secret rotated and we didn't update `STRIPE_WEBHOOK_SECRET` in k8s
2. A migration is running and the relevant table is briefly locked
3. A bug we shipped — roll back, then debug

### `dunning_email_send_failures > 10/hr`

Postmark API is rate-limiting us, or our IP is on a blocklist. Check the Postmark dashboard, then if needed swap to the SES fallback by setting `DUNNING_EMAIL_PROVIDER=ses` in the billing service config.

## Refund policy

Refunds under $50 can be issued by support without engineering involvement. Anything over $50 goes through the founders. The actual refund call goes through `POST /admin/billing/refund` — there is no Stripe-direct path. This is enforced in code so we always have an audit trail.

## Known gotchas

- **Plan downgrade refunds**: prorated based on the unused portion of the current period. This is computed at midnight UTC, not at the moment of downgrade.
- **Invoice numbering**: monotonic, no gaps. If you ever need to cancel an invoice, *void* it instead of deleting it. EU VAT auditors hate gaps.
- **Connection pool**: the billing service holds 12 connections per replica. Don't bump this without coordinating with the platform team — the global Postgres ceiling is documented in `04-architecture-decisions.md`.
