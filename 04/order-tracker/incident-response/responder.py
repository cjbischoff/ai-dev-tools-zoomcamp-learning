"""Incident responder service for Order Tracker.

Listens on ``POST /alerts`` (port 8001) for Grafana webhook notifications,
saves the alert information, runs a headless agent to investigate, and returns
the agent's response.
"""

from __future__ import annotations

import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


INCIDENTS_DIR = Path(os.getenv("INCIDENTS_DIR", "incident-response/incidents"))
AGENT_SCRIPT = Path(os.getenv("AGENT_SCRIPT", "incident-response/agent.py"))

app = FastAPI(title="Responder")


@app.post("/alerts")
async def handle_alert(request: Request) -> JSONResponse:
    """Receive an alert from Grafana and dispatch the headless agent."""
    payload = await request.json()
    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"

    # Save the alert payload
    incidents_dir = INCIDENTS_DIR
    incidents_dir.mkdir(parents=True, exist_ok=True)
    incident_file = incidents_dir / f"{incident_id}.json"
    record = {
        "incident_id": incident_id,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "alert": payload,
    }
    incident_file.write_text(json.dumps(record, indent=2))

    # Run the headless agent
    print(f"[responder] Incident {incident_id} — starting agent")
    try:
        result = subprocess.run(
            ["python3", str(AGENT_SCRIPT), str(incident_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        agent_output = result.stdout
        if result.returncode != 0:
            agent_output = f"Agent error: {result.stderr}"
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        agent_output = f"Agent failed: {exc}"

    # Save agent output
    output_file = incidents_dir / f"{incident_id}_response.txt"
    output_file.write_text(agent_output)

    print(f"[responder] Incident {incident_id} — agent finished")
    return JSONResponse(
        content={
            "incident_id": incident_id,
            "agent_response": agent_output,
            "response_log": str(output_file),
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
