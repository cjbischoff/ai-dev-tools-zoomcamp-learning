# Security Audit Brief — Agent Relay

## Scope

| Item | Target |
|---|---|
| Application | `04/agent-relay/` (FastAPI + SQLAlchemy + SQLite) |
| Responder | Headless coding agent as on-call first responder |
| Telemetry stack | OpenTelemetry Collector, Prometheus, Loki, Tempo, Grafana |

## Methodology

Three layers, run in order:

1. **Deterministic scanner** — Semgrep rules against `04/agent-relay/`:
   - `python.lang.security` — injection, eval, shell injection
   - `python.lang.maintainability` — hardcoded secrets, debug endpoints
   - `python.flask.security` — path traversal, open redirect (applies to FastAPI)
   - `supply-chain` — known-vulnerability dependencies (osv)

2. **Model review** — The headless responder (or chat agent) reviews Semgrep
   findings, adds context, and flags any pattern the scanner missed.

3. **Human validation** — Each finding is reviewed and dispositioned by a human
   operator (the module author).  `accepted`, `mitigated`, or `false_positive`.

## Deliverables

- `runs/semgrep.json` — raw Semgrep output
- `runs/findings.md` — consolidated findings with model review and disposition
- `capability-table.md` — inventory of what the responder can access

## Schedule

Run after every deployment that touches `04/agent-relay/`.
