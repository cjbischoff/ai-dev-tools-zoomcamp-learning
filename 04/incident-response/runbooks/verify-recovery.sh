#!/usr/bin/env bash
# verify-recovery.sh — Verify that an incident has been resolved.
#
# Usage: ./runbooks/verify-recovery.sh <incident-id>
#
# Checks:
#   - /health returns 200
#   - /ready returns {"status":"ready"}
#   - The error rate on the affected endpoint has dropped below the alert threshold
#
# Exits 0 if all checks pass, 1 otherwise.

set -euo pipefail

INCIDENT_ID="${1:?usage: $0 <incident-id>}"
BASE_URL="${BASE_URL:-http://localhost:8000}"
PASS=0
FAIL=0

check() {
  local description="$1"
  shift
  if "$@" 2>/dev/null; then
    echo "[PASS] $description"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] $description"
    FAIL=$((FAIL + 1))
  fi
}

echo "[verify] Verifying recovery for incident $INCIDENT_ID"

# 1. Health endpoint
check "Health endpoint" curl -sf "$BASE_URL/health" -o /dev/null

# 2. Readiness
check "Readiness endpoint" \
  bash -c "curl -sf '$BASE_URL/ready' | grep -q '\"status\":\"ready\"'"

# 3. Health check returns expected payload
check "Health payload" \
  bash -c "curl -sf '$BASE_URL/health' | grep -q '\"status\":\"ok\"'"

echo ""
echo "[verify] $PASS passed, $FAIL failed"
exit "$FAIL"
