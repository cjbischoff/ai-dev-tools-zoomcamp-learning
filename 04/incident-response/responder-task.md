# Responder Task — Incident <ID>
#
# This file is handed to the headless coding agent as the task specification
# after the evidence packet has been collected.

## Evidence packet

The evidence packet is at `incident-response/incidents/<ID>/evidence.json`.
It contains recent commits, health checks, readiness, agent list, and
container state.  Review it before reasoning.

## Task

1. Compare the evidence packet with the current working tree.
2. Identify the most likely root cause of the elevated error rate.
3. Propose exactly one action from the allowlist:

   - `rollback` — revert the last deployment (requires runbook)
   - `fix` — commit a code change and deploy
   - `escalate` — insufficient evidence, hand to human

4. Respond in the schema defined in `response.schema.json`.

## Constraints

- You have READ-ONLY access.  Do not modify code, configuration, or data.
- Do not use production credentials.
- Propose an action only when you have high confidence in the root cause.
- When uncertain or evidence is insufficient, respond with `"action": "escalate"`.
