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

### Q2: The telemetry pipeline

**Answer:** OpenTelemetry

The module's concrete stack is "OpenTelemetry into Prometheus, Loki, and Tempo, with Grafana on top." OpenTelemetry is the vendor-neutral instrumentation standard for generating, collecting, and exporting telemetry data. OpenAPI (API contracts), OAuth (auth), and OpenSSL (crypto) are unrelated.

### Q3: Dashboards

**Answer:** Grafana

"Grafana on top" — the module wires OpenTelemetry Collector feeding Prometheus, Loki, and Tempo, all viewed together in Grafana. pgAdmin is a Postgres admin tool, Excel is a spreadsheet, and VS Code is an editor.

### Q4: Alerts

**Answer:** Real user impact, with context to start investigating

The module says: "Write one alert that represents real user impact and carries enough context in its payload to act on." CPU spikes, every log line, or deployment notifications are not user-impact alerts.

### Q5: Evidence first

**Answer:** With read-only, allowlisted queries

"Collect a bounded, repeatable evidence packet with read-only, allowlisted queries before any model gets involved." Full production admin credentials, trial-and-error on the database, or letting the model decide what to look at all violate the evidence-before-model principle.

### Q6: The agent responder

**Answer:** The autonomy policy and allowlists — code outside the model

"What it does not get is general production credentials. A model supplies confidence; code outside the model enforces permission." Model confidence, alert severity, or autonomous action are explicitly rejected — the module gates action behind allowlists and autonomy levels.

### Q7: Security audit

**Answer:** Semgrep

The module specifies: "Run recurring security audits that combine a deterministic scanner (Semgrep), model review, and human validation." Pytest (unit tests), Playwright (browser tests), and Terraform (infrastructure) serve different purposes.
