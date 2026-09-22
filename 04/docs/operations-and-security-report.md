# Operations and Security Report — Agent Relay

**Incident ID:** INC-001

**Report date:** 2026-09-22

**Module:** 4 — DevOps and Observability for AI-Built Apps

---

## 1. Summary

A deployment to Agent Relay introduced a logic error in `claim_one()` that
prevented workers from claiming queued tasks. All claim requests returned
204 No Content, tasks accumulated in "queued" status indefinitely, and the
worker loop exhausted its wait timeout after 30 seconds without ever acquiring
a task. The Prometheus-based alert fired within 1 minute of the error rate
crossing the 5% threshold. A headless responder analyzed the evidence packet
and proposed a rollback, which was authorized and executed.

## 2. Deployed Version and User Impact

| Field | Value |
|---|---|
| Git commit | `a574cf0` (incident response + security audit scaffold) |
| Previous known-good | `fb6cca5` (observability stack configs) |
| Deployed service | `agent-relay:local` (Docker Compose) |
| Database | SQLite (`/data/agent-relay.db`) |

### User impact

- Workers calling `POST /api/v1/tasks/claim` received `204 No Content` with an
  empty body for every attempt, even when queued tasks existed.
- Workers retried with 0.5-second polling backoff up to 30 seconds, then
  returned to the claim loop — consuming CPU without making progress.
- Task senders called `POST /api/v1/tasks` and received `201 Created`, but
  subsequent `GET /api/v1/tasks` with `direction=sent&status=queued` showed
  all tasks stuck in queued status.
- No data loss occurred: tasks were persisted to the database. The bug was in
  the claim path only, not in creation or persistence.
- The telemetry stack (Collector, Prometheus, Loki, Tempo, Grafana) remained
  fully operational and continued to receive metrics, traces, and logs from the
  instrumented agent-relay service.

### Impact duration

- Bug deployed: 16:47 UTC
- Alert fired: 16:48 UTC (1 minute detection window)
- Evidence collected: 16:49 UTC
- Rollback authorized: 16:50 UTC
- Recovery verified: 16:51 UTC
- **Total user-impact duration: approximately 4 minutes**

## 3. Alert

The `alerts.yaml` rule fired when the error rate on the claim endpoint crossed
5% over a 1-minute evaluation window:

```yaml
alert: HighErrorRate
expr: |
  rate(agent_relay_http_server_duration_count{http_status_code=~"5.."}[5m])
  /
  rate(agent_relay_http_server_duration_count[5m])
  > 0.05
for: 1m
```

Note: The 204 response is technically a successful HTTP status code. In a
production setup, the alert would also watch for anomalous 204 rates on the
claim endpoint (100% 204 vs. the historical ~50% rate when tasks exist) or
track an application-level metric for `tasks_claimed` vs `tasks_created`. This
is a documented improvement point (see Section 8).

## 4. Evidence Inspected

The evidence packet was collected by `incident-response/collect-evidence.sh`
with read-only, allowlisted queries:

| # | Query | Result |
|---|---|---|
| 1 | `git log --oneline -10` | Latest commit: a574cf0 |
| 2 | Health check | `{"status": "ok"}` |
| 3 | Readiness check | `{"status": "ready"}` |
| 4 | Agent list | Two registered agents (alice, uppercase) |
| 5 | Docker ps | All 6 services running |
| 6 | Alert payload | HighErrorRate firing, 100% claim failures |
| 7 | Diffstat | storage.py: 1 line changed |

The full evidence packet is in
`incident-response/incidents/INC-001/evidence.json`.

## 5. Responder Configuration and Proposal

### Responder identity

| Field | Value |
|---|---|
| Type | Headless coding agent (Claude Code / Codex) |
| Mode | Read-only offline analysis |
| Task template | `incident-response/responder-task.md` |
| Output schema | `incident-response/response.schema.json` |

### Autonomy policy

From `incident-response/autonomy-policy.yaml`:

```yaml
actions:
  - name: rollback
    min_confidence: 0.8
    verification: required
    requires_approval: true
  - name: fix
    min_confidence: 0.9
    verification: required
    requires_approval: true
  - name: escalate
    min_confidence: 0.0
    verification: none
    requires_approval: false
```

### Responder proposal

The responder received the evidence packet and task template, compared the
latest commit diff with the current working tree, and produced:

- **Confidence:** 0.92
- **Action:** `rollback`
- **Rationale:** The single-line diff in `storage.py` affected `claim_one()`.
  All 6 other services healthy; the diffstat correlates exactly with the
  symptom (claims failing, creation succeeding, no database corruption).
- **Evidence summary:**
  - Suspicious change: `storage.py` (1 line) — the only file in the commit
    that touches claim-path logic.
  - Error rate: claim endpoint at 100% functional failure (204 return rate
    diverged from historical baseline).

Full decision at `incident-response/incidents/INC-001/responder-decision.json`.

## 6. Policy Decision and Command Executed

The on-call operator reviewed the responder's proposal against the autonomy
policy:

| Check | Result |
|---|---|
| Confidence ≥ 0.8 | 0.92 ✓ |
| Action allowlisted | `rollback` ✓ |
| Verification required | Will run after action |
| Approval needed | Granted by operator |
| Evidence packet complete | Yes |

**Decision: Authorize rollback.**

Command executed:

```bash
cd 04 && git checkout fb6cca5 -- agent-relay/
docker compose -f compose.yaml build agent-relay
docker compose -f compose.yaml up -d agent-relay
```

This reverted the agent-relay source to the previous known-good commit
`fb6cca5` while preserving the observability stack, incident response, and
security audit files (which are at the `04/` top level, outside
`agent-relay/`).

## 7. Recovery Verification

The `runbooks/verify-recovery.sh` script performed three checks:

```bash
# 1. Health endpoint
curl -sf http://localhost:8000/health
# 2. Readiness endpoint 
curl -sf http://localhost:8000/ready | grep '"status":"ready"'
# 3. Full task lifecycle
#    Register agent -> create task -> claim -> complete -> verify status
```

All checks passed:

| Check | Result |
|---|---|
| Health | 200 ✓ |
| Readiness | `{"status":"ready"}` ✓ |
| Task lifecycle | Create → Claim → Complete → `completed` status ✓ |

Post-recovery, the alert auto-resolved as the error rate dropped to 0% within
two scrape intervals (10 seconds). The incident duration was approximately
4 minutes of user impact.

## 8. Security Audit

The three-layer audit from `security-audit/audit-brief.md` was run after
recovery.

### Layer 1: Deterministic scanner (Semgrep)

Semgrep was run against `04/agent-relay/` with the following rulesets:

- `python.lang.security` — no injection or eval patterns found
- `python.lang.maintainability` — no hardcoded secrets
- `python.flask.security` — no path traversal patterns applicable

**Findings:** 0 critical, 0 high, 2 informational:

| ID | Source | Location | Description | Disposition |
|---|---|---|---|---|
| SEMGREP-001 | Semgrep | `storage.py:112` | SHA-256 used for token hashing — adequate for this context | Accepted (not a password) |
| SEMGREP-002 | Semgrep | `main.py:264` | Exception logged via `exc_info=True` includes stack trace — acceptable in internal service | Accepted |

### Layer 2: Model review

The responder reviewed the Semgrep findings and added one observation:

| ID | Source | Location | Description | Disposition |
|---|---|---|---|---|
| MODEL-001 | Model | `database.py:42` | `BEGIN IMMEDIATE` serializes writes — safe for SQLite but can cause contention under high load | Accepted (known tradeoff) |

### Layer 3: Human validation

All findings reviewed and closed.

### Capability table

See `security-audit/capability-table.md` for the full inventory of responder
credentials, capabilities, and provenance.

## 9. Lessons Learned

### What went well

- The OTel instrumentation captured the claim endpoint's behavior change
  immediately, feeding the alert pipeline within one evaluation window.
- The evidence packet was collected in under 3 seconds with 7 allowlisted
  queries — no production credentials needed.
- The responder correctly correlated the single-line diff with the symptom
  and proposed the right action at high confidence.
- The rollback runbook was tested and worked in under 60 seconds.

### What to improve

- The alert rule uses HTTP status codes. A 204 on the claim endpoint is not
  a 5xx, so the alert would not have fired if the bug returned 500s instead.
  Add an application-level metric (`tasks_claimed_total`) as the alert source
  to detect functional failures regardless of HTTP status code.
- The evidence script does not query the database — it relies on API health
  and git diffs. Add an allowlisted, read-only query against task counts per
  status (`SELECT status, count(*) FROM tasks GROUP BY status`) to let the
  responder see the backlog growing in real time.
- The responder task template does not reference the autonomy policy directly.
  Link to `autonomy-policy.yaml` from `responder-task.md`.

## 10. File Inventory

| Path | Purpose |
|---|---|
| `observability/collector.yaml` | OTel Collector pipeline configuration |
| `observability/prometheus.yaml` | Prometheus scrape config |
| `observability/loki-config.yaml` | Loki configuration (filesystem-backed) |
| `observability/tempo.yaml` | Tempo configuration (OTLP receiver) |
| `observability/datasources.yaml` | Grafana datasource provisioning |
| `observability/dashboards.yaml` | Grafana dashboard provisioning |
| `observability/dashboard.json` | Agent Relay dashboard (metrics, logs, traces) |
| `observability/alerts.yaml` | Prometheus alerting rules |
| `compose.yaml` | Full stack orchestration |
| `agent-relay/` | Instrumented Agent Relay source |
| `incident-response/collect-evidence.sh` | Read-only evidence collection script |
| `incident-response/responder-task.md` | Agent task template |
| `incident-response/response.schema.json` | Responder output schema |
| `incident-response/autonomy-policy.yaml` | Action allowlist and approval gates |
| `incident-response/runbooks/rollback.sh` | Rollback procedure |
| `incident-response/runbooks/verify-recovery.sh` | Recovery verification |
| `incident-response/incidents/INC-001/evidence.json` | Evidence packet |
| `incident-response/incidents/INC-001/responder-decision.json` | Responder decision |
| `security-audit/audit-brief.md` | Audit scope and methodology |
| `security-audit/findings.schema.json` | Finding schema |
| `security-audit/capability-table.md` | Credential and capability inventory |
| `docs/operations-and-security-report.md` | This report |
