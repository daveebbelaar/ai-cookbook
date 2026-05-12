# Customer support playbook

This is for the support team. Engineering reads it too because half of what we ship lands in here as a ticket within a week.

## Tools

- **Zendesk** — ticket system of record. Every customer-facing thing goes through here.
- **Linear** — bug tracker. When a ticket needs engineering, we file a Linear issue and link it back to the Zendesk ticket.
- **Stripe (read-only)** — for verifying payment status. Most billing questions can be answered without engineering by checking Stripe directly.
- **Internal admin dashboard** at `admin.nimbuslabs.internal` — for impersonation, refunds, plan changes.

## Severity

| Level | Definition | First response | Resolution target |
|---|---|---|---|
| P0 | Customer can't access their account, or production data appears lost | 15 min | 4 hr |
| P1 | A core feature is broken for one or more customers | 1 hr | 1 business day |
| P2 | A non-core feature is broken, or a customer needs a manual fix | 4 hr | 3 business days |
| P3 | Cosmetic, "how do I" questions, feature requests | 1 business day | 5 business days |

## When to escalate to engineering

Escalate immediately if:

- Multiple customers are reporting the same issue within an hour
- The issue references a specific error code containing the word `internal_server_error`
- A customer claims data loss
- A security-adjacent concern (account takeover, unauthorized access, leaked data)

For everything else, try the runbook first.

## Common requests

### "I was charged twice"

99% of the time this is a payment retry from Stripe after a transient failure, and only one charge actually settled. Check in Stripe → Customer → Payments. If both succeeded, refund one through `admin.nimbuslabs.internal/billing/refund`.

### "Can you reset my password / 2FA?"

Always verify identity first via the email on file. Reset via admin dashboard. Document the reason on the customer's record.

### "I want to cancel"

Don't argue. Process the cancellation. Schedule a follow-up with the founder if the customer was paying more than $500/month — but only as a check-in, not as a save attempt.

### "Why is my dashboard slow?"

Check the dashboard's status indicator first. If everything's green, ask the customer their region — the dashboard is fastest in EU and US East. Other regions go through a CDN with 80-150ms added latency. This is documented at the bottom of our marketing page.

### "Where's my export?"

Exports are queued, not synchronous. Most finish in under 5 minutes; very large accounts can take up to an hour. If it's been more than an hour, escalate to engineering — the export worker may be stuck.

## Logging your work

Every ticket gets a one-line resolution note when you close it. "Customer issue resolved" is not a resolution note. "Refunded $42 duplicate charge — ticket #ZD-9912, see Stripe ch_xxx" is a resolution note.
