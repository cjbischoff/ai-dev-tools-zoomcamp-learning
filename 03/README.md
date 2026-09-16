# Agent Relay

Agent Relay is a small messaging system for software agents. An agent sends a task to another agent, a worker claims the task, and the worker acknowledges the result. The database stores the messages and their delivery attempts. A small dashboard lets you watch the message lifecycle.

Built for the [AI Dev Tools Zoomcamp 2026](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp) — Module 3: Test, Containerize, and Deploy.

**Stack:** FastAPI + SQLAlchemy + SQLite (starter) / PostgreSQL (deployment)

## Quick Start

```bash
cd agent-relay
uv sync
uv run uvicorn main:app --reload
```

Open http://127.0.0.1:8000/ for the dashboard.

## Running

| Mode | Command |
|---|---|
| Dev server | `uv run uvicorn main:app --reload` (port 8000) |
| Docker | `docker build -t agent-relay:local . && docker run -p 8000:8000 agent-relay:local` |
| Compose + Postgres | `docker compose up --build` (port 8000) |
| Kubernetes (kind) | `kubectl apply -f k8s/` (port-forward svc/agent-relay 8000:8000) |

## Structure

| Path | Purpose |
|---|---|
| `agent-relay/` | FastAPI application (main.py, routes, storage, models) |
| `agent-relay/tests/` | Integration tests for the task lifecycle |
| `agent-relay/k8s/` | Kubernetes manifests (PostgreSQL + Agent Relay) |
| `agent-relay/.github/workflows/` | CI/CD pipeline |
| `agent-relay/Dockerfile` | Multi-stage container build |
| `agent-relay/compose.yaml` | Docker Compose with PostgreSQL |
| `README.md` | This file |

---

## Homework Answers

### Q1: Understand the project

Forked [alexeygrigorev/agent-relay](https://github.com/alexeygrigorev/agent-relay) into `03/agent-relay/`. Installed deps, started the server, registered two agents, and sent/claimed/completed a task. The sender sees `"status": "completed"` with the output.

**Architecture:** Agents claim tasks from a DB through an HTTP API.

### Q2: Register agents and test the task flow

Registered two agents, exchanged a task (queued → processing → completed), and verified the result in the dashboard. Created an API integration test at `tests/test_integration.py` that automates the full register → send → claim → complete → verify flow using FastAPI TestClient.

**Test result:** `6 passed in 0.46s` (4 starter + 2 integration)

**Task status after completion:** `completed`

### Q3: Containerization

Created a multi-stage `Dockerfile` (builder syncs deps with uv, final stage runs uvicorn on `0.0.0.0`). Built `agent-relay:local`, ran with `-p 8001:8000`, repeated the full task flow successfully.

**Port publishing option:** `-p`

### Q4: Docker Compose and PostgreSQL

Created `compose.yaml` with a `postgres` service (PostgreSQL 17 Alpine) and the Agent Relay service. Fixed `immediate_transaction()` in `database.py` to skip `BEGIN IMMEDIATE` for PostgreSQL, and added `.with_for_update(skip_locked=True)` in `claim_one()` for PostgreSQL row locking. Verified data is stored in PostgreSQL via `psql`.

**DB hostname:** `postgres` (Docker Compose service name)

### Q5: Deploy to Kubernetes

Installed kind via brew, created `kind-agent-relay` cluster. Created `k8s/` manifests (PostgreSQL PVC + Deployment + Service, Agent Relay Deployment with readiness/liveness probes + Service). Loaded the image into kind, deployed, port-forwarded, and verified the full task flow.

**K8s resource for replicas:** `Deployment`

### Q6: CI/CD

Created `.github/workflows/ci.yml` with `test` (PostgreSQL service + pytest) and `deploy` (build + kind load + kubectl set image + rollout) jobs. Ran locally with act using `--network host` and `--container-daemon-socket`. Updated the dashboard heading to **Agent Relay v2**, re-ran the workflow, and confirmed the v2 heading in the deployed dashboard.

**If a test fails:** Keep the existing version running and stop the deployment (`needs: [test]` gate).
