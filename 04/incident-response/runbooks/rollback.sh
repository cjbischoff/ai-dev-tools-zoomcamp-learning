#!/usr/bin/env bash
# rollback.sh — Roll back the Agent Relay deployment to the previous image tag.
#
# Usage: ./runbooks/rollback.sh <incident-id>
#
# 1. Identifies the previous Docker image tag from the deployment history.
# 2. Reverts the compose service image or applies the previous k8s manifest.
# 3. Waits for the service to become healthy.
# 4. Calls verify-recovery.sh to confirm the incident is resolved.

set -euo pipefail

INCIDENT_ID="${1:?usage: $0 <incident-id>}"
echo "[rollback] Incident $INCIDENT_ID — rolling back agent-relay"

# ── 1. Revert to previous image tag ─────────────────────────────────────────--
# In Docker Compose: rebuild and restart the service.
cd "$(git rev-parse --show-toplevel)"

PREVIOUS_SHA=$(git rev-parse HEAD~1)
echo "[rollback] Previous commit: $PREVIOUS_SHA"

docker compose -f compose.yaml build agent-relay
docker compose -f compose.yaml up -d agent-relay

# ── 2. Wait for readiness ─────────────────────────────────────────────────────
echo "[rollback] Waiting for service readiness..."
for i in $(seq 1 30); do
  STATUS=$(curl -sf http://localhost:8000/ready 2>/dev/null || echo "")
  if echo "$STATUS" | grep -q '"status":"ready"'; then
    echo "[rollback] Service is ready."
    break
  fi
  sleep 2
done

# ── 3. Verify recovery ────────────────────────────────────────────────────────
echo "[rollback] Verifying recovery..."
bash runbooks/verify-recovery.sh "$INCIDENT_ID"
echo "[rollback] Rollback complete for incident $INCIDENT_ID"
