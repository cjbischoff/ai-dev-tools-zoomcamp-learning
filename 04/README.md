# Operations and Security — Module 4

Module 4 work for the AI Dev Tools Zoomcamp (2026): DevOps and Observability for AI-Built Apps. Builds on the deployed Agent Relay app from Module 3.

**Loop:** change → observe user impact → alert with context → investigate from evidence → authorize a bounded response or escalate → verify recovery → audit the code and the response trail.

**Stack:** OpenTelemetry → Collector → Prometheus / Loki / Tempo → Grafana, plus a headless coding agent (read-only first responder) behind an allowlisted autonomy policy.

## Deliverables (planned)

| Path | Purpose |
|---|---|
| `observability/` | collector.yaml, compose.yaml, dashboard.json, alerts.yaml |
| `incident-response/` | collect-evidence.sh, responder task + schema, autonomy policy, runbooks, incidents |
| `security-audit/` | audit brief, findings schema, capability table, runs |
| `docs/operations-and-security-report.md` | Final report: one incident ID reconstructs the whole loop |

## Homework Answers

Answers are added and committed one question at a time as each is reviewed and approved.

### Q1: Instrumentation
