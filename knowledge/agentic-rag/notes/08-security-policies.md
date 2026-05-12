# Security policies

Short, practical, and updated when reality changes.

## Secrets

- All secrets live in 1Password (team vault) or AWS Secrets Manager. Never in Git. Never in Slack. Never in Notion.
- New secrets get a documented owner (a person, not a team). The owner is responsible for rotation.
- Default rotation: 90 days for human-issued credentials, 30 days for service tokens with broad scope, automatic for everything we can automate.
- Detect leaks with `gitleaks` in pre-commit and on every PR.

## Authentication

We use Google Workspace SSO for internal tools. All staff accounts require hardware-key 2FA — TOTP alone is not sufficient for the engineering org.

For our customer-facing product, we offer:

- Magic-link email auth (default)
- Email + password with TOTP 2FA
- SSO (SAML, for enterprise plans)

We do not offer password-only auth without 2FA. We do not store passwords; everything goes through Auth0.

## Data classification

- **Public**: marketing site, blog, public docs. Anyone, anywhere.
- **Internal**: this wiki, deploy logs, internal Slack. Employees and contractors.
- **Confidential**: customer data, billing records, deploy keys. Need-to-know.
- **Restricted**: source-of-truth keys, root admin tokens. Two-person rule for access; logged.

## Vulnerability disclosure

We accept reports at security@nimbuslabs.example. Triage SLO: 24 hours for first response, 7 days for resolution path. Researchers acting in good faith receive safe harbor; we publish a coordinated disclosure timeline once the fix is shipped.

## Incident classification (security-specific)

| Class | Examples | Response |
|---|---|---|
| S0 | Confirmed data breach, active exploitation | All-hands, founder pages out, legal involvement immediately |
| S1 | Plausible breach indicators, anomalous access patterns | On-call security lead + senior eng, founder notified within 1 hour |
| S2 | Vulnerability discovered, no evidence of exploitation | Triaged into next sprint, deadline based on severity |
| S3 | Theoretical or low-impact issue | Logged, no immediate action |

## Things you should never do

- SSH into production hosts. We don't do persistent SSH access; use the bastion + audit-logged shell sessions.
- Copy customer data to a personal machine. Even for debugging.
- Disable a security control "temporarily" without a documented re-enable date and an incident ticket.
- Share a 1Password item via a link that doesn't expire.

## Things you should always do

- Lock your laptop. Even at home. We had a household pet trigger an unauthorized API call once.
- Run security scans before merging. The CI runs `bandit` and `safety check`; treat their warnings as blocking unless you have a documented exception.
- File a security ticket if you see something weird, even if you're 90% sure it's nothing. The other 10% is what matters.
