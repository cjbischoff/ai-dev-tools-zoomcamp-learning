# DevOps and Observability — Module 4

Work for the [AI Dev Tools Zoomcamp 2026](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp) —
Module 4: DevOps and Observability for AI-Built Apps. Based on the
[Order Tracker](https://github.com/alexeygrigorev/order-tracker) starter app.

**Stack:** FastAPI + SQLite + OpenTelemetry → Collector → Prometheus / Loki / Tempo → Grafana, plus an incident responder on port 8001.

## Structure

| Path | Purpose |
|---|---|
| `order-tracker/` | Instrumented Order Tracker app + all homework artifacts |
| `order-tracker/app/` | FastAPI app with OpenTelemetry instrumentation |
| `order-tracker/observability/` | OTel Collector, Prometheus, Loki, Tempo, Grafana configs |
| `order-tracker/incident-response/` | Responder service + headless agent for incident handling |
| `README.md` | This file — homework answers |

## Quick Start

```bash
cd order-tracker
docker compose up --build -d --wait
```

Open http://localhost:8000 (app), http://localhost:3000 (Grafana).

## Homework Answers

### Q1: Run the app

Health check returns `{"status":"ok"}`.

### Q2: Instrument one endpoint

Looked up `standard-1001` → HTTP status code in the metric: **200**.

The app was instrumented with OpenTelemetry (traces, metrics, logs) exporting to console. The metric includes route and HTTP status code labels (`http.target`, `http_status_code`).

### Q3: Build the telemetry pipeline

Looked up `standard-1002` (does not exist) → HTTP status code in the metric: **404**.

Full pipeline configured:
- App exports OTLP to Collector
- Collector fans out: metrics → Prometheus, traces → Tempo, logs → debug
- Grafana provisions datasources and dashboard automatically

### Q4: Configure the alert

Configured Grafana managed alert rule `High5xxRate`. Expression:
```
rate(order_tracker_http_server_duration_milliseconds_count{http_status_code=~"5.."}[1m]) > 0
```
`noDataState: OK` handles periods with no 5xx responses. With no 5xx errors the alert state is **Normal** (inactive).

### Q5: Build the automatic responder

Created `incident-response/responder.py` — FastAPI service on port 8001 with `POST /alerts`. When alert arrives, it saves the payload and dispatches a headless agent (`incident-response/agent.py`).

Test alert sent. Agent responded — last line: `Analysis complete. No action needed — this is a test notification.`

### Q6: Watch the agent fix the incident

`curl http://localhost:8000/api/orders/express-1002` returned **500 Internal Server Error**.

**Root cause:** The express delivery date calculation used `placed_at.replace(day=placed_at.day + 2)`. When `placed_at` is the last day of a month (Aug 31 for the seed data), `day + 2` exceeds the month boundary (33), causing `ValueError`.

**Fix:** Changed to `placed_at + timedelta(days=2)`.

After fix: `curl http://localhost:8000/api/orders/express-1002` returns **200 OK** with `estimated_delivery: "2026-09-02"`.

## Deliverables

| File | Purpose |
|---|---|
| `app/otel.py` | OTel setup (console or OTLP export) |
| `app/main.py` | Instrumented app + date bug fix |
| `pyproject.toml` | OTel SDK dependencies |
| `compose.yaml` | 7 services: app, collector, Prometheus, Loki, Tempo, Grafana, responder |
| `observability/` | 8 config files for the telemetry stack |
| `incident-response/responder.py` | POST /alerts service on port 8001 |
| `incident-response/agent.py` | Headless incident analysis agent |
| `incident-response/incidents/` | Recorded test incidents |
