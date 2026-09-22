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

**Answer:** Metrics, logs, and traces

Observability rests on three signal types — metrics (quantitative measurements), logs (structured event records), and traces (end-to-end request paths). The module instruments one endpoint end to end with all three via OpenTelemetry, without leaking secrets. CPU graphs alone are infrastructure monitoring, not observability — they cannot tell you which endpoint failed or why.

**Evidence:** Module intro: "Instrument one endpoint end to end with OpenTelemetry — metrics, traces, and structured logs — without leaking secrets."
