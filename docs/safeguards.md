# Safeguards

- Read-only research and drafting run automatically.
- Email, ticket, and meeting effects require explicit approval.
- Approval is scoped to the exact canonical action arguments.
- Changed arguments require a new review.
- Idempotency prevents repeat execution during retries.
- Disabled tools fail closed.
- Page targets must be public HTTP(S) URLs; local/private networks are rejected.
- Web content is evidence, never system instruction.
- Provider retries are bounded and failures return controlled messages.
- Known sensitive fields are redacted from results and traces.
- Mock adapters are the default and report `external_effect: false`.

For a real deployment, add authenticated reviewers, policy-based authorization, PostgreSQL transactions, an isolated egress proxy, encrypted secrets, rate limits, and monitored integration adapters.

