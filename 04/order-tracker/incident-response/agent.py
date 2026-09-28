#!/usr/bin/env python3
"""Headless agent for incident response.

Receives an incident file path, reads the alert payload, and produces a
structured analysis.  Simulates what a real coding agent (Codex / Claude Code)
would do when called as a read-only first responder.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def analyze(incident: dict) -> str:
    """Analyse the alert and return a structured response."""
    alert = incident.get("alert", {})
    alerts = alert.get("alerts", [alert])
    lines = [
        "=" * 60,
        "INCIDENT RESPONDER — ANALYSIS",
        "=" * 60,
        f"Incident ID:  {incident['incident_id']}",
        f"Received at:  {incident['received_at']}",
        f"Analyzed at:  {datetime.now(timezone.utc).isoformat()}",
        "",
        "Alert Summary:",
    ]

    for a in alerts:
        labels = a.get("labels", {})
        annotations = a.get("annotations", {})
        lines.append(f"  - Alert:     {labels.get('alertname', 'unknown')}")
        lines.append(f"    Status:    {a.get('status', 'unknown')}")
        lines.append(f"    Severity:  {labels.get('severity', 'none')}")
        lines.append(f"    Endpoint:  {labels.get('http_target', 'unknown')}")
        lines.append(f"    Summary:   {annotations.get('summary', 'none')}")

    lines.extend(
        [
            "",
            "Evidence Collection:",
            "  1. Recent deploys — git log --oneline -10",
            "  2. Health check  — GET /healthz",
            "  3. Error rate    — Prometheus / Loki query",
            "  4. Logs          — docker compose logs --tail=50",
            "",
            "Root Cause Analysis:",
            "  This is a test notification. No incident to fix.",
            "  In a real incident, the agent would compare the alert's",
            "  endpoint and error rate with recent deployment diffs.",
            "",
            "Proposed Action:",
            "  escalate (test notification — no action needed)",
            "",
            "---",
            "Analysis complete. No action needed — this is a test notification.",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python agent.py <incident-file>", file=sys.stderr)
        sys.exit(1)

    incident_file = sys.argv[1]
    with open(incident_file) as f:
        incident = json.load(f)

    output = analyze(incident)
    print(output)


if __name__ == "__main__":
    main()
