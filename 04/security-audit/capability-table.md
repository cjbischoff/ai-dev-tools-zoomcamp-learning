# Capability Table — Agent Relay Responder

Inventory of the headless responder's capabilities, credentials, and provenance,
based on the Snyk Agent Scan pattern defined in the module.

## Identity

| Field | Value |
|---|---|
| **Agent** | Headless coding agent (Claude Code / Codex) |
| **Version** | Determined by runtime environment |
| **Runtime** | `uv run --directory agent-relay` |
| **Execution mode** | Read-only, offline analysis of evidence packet |

## Credentials

| Credential | Has Access | Stored | Notes |
|---|---|---|---|
| `RELAY_ENROLLMENT_SECRET` | No | N/A | Not needed for analysis |
| DB path (`RELAY_DATABASE_URL`) | No (responder) / Yes (app) | `compose.yaml` env | Responder never connects to DB |
| OTLP endpoint | No | N/A | Collector accepts from app, not responder |
| Git credentials | No (CI) / Yes (local) | N/A | Responder analyses diff only |

## Capabilities

| Capability | Allowed | Gated By | Notes |
|---|---|---|---|
| Read evidence packet | Yes | File existence | Bounded JSON from `collect-evidence.sh` |
| Read git log | Yes | Read-only filesystem | Analyses recent commits for correlation |
| Read source code | Yes | Read-only filesystem | Investigates suspicious changes |
| Propose rollback | Yes | Autonomy policy | Requires approval |
| Propose fix | Yes | Autonomy policy | Requires approval; high confidence only |
| Escalate | Yes | Autonomy policy | Always allowed |
| Modify code | No | Read-only mode | Responder has no write access |
| Modify config | No | Read-only mode | Responder has no write access |
| Access database | No | No credentials | Responder cannot authenticate to the DB |
| Network egress | No | Sandbox | No network access from the responder |

## Provenance

| Artifact | Source | Integrity |
|---|---|---|
| `otel_setup.py` | Created in this module | Git-tracked |
| `collect-evidence.sh` | Created in this module | Git-tracked |
| `responder-task.md` | Created in this module | Git-tracked |
| `autonomy-policy.yaml` | Created in this module | Git-tracked |
| Container images | Docker Hub (otel, grafana, prom) | Tag-pinned in compose.yaml |
