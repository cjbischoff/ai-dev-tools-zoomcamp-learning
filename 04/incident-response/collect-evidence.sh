#!/usr/bin/env bash
# collect-evidence.sh — Read-only evidence collection for incident response.
#
# Usage: ./collect-evidence.sh <incident-id> [--base-url <url>]
#
# Collects a bounded, repeatable evidence packet for the given incident:
#   - Recent deploys (git log)
#   - Current endpoint error rates (API health + ready checks)
#   - Recent log lines (if docker/Loki accessible)
#   - Deployed image tags
#
# Outputs a structured evidence bundle to stdout in JSON Lines format.
# The bundle is intended for consumption by a responder agent (or human).
#
# This script uses ONLY read-only, allowlisted queries.
# It does NOT have or use production admin credentials.

set -euo pipefail

INCIDENT_ID="${1:?usage: $0 <incident-id> [--base-url <url>]}"
BASE_URL="${2:-http://localhost:8000}"

echo "{\"incident_id\": \"$INCIDENT_ID\", \"collected_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"evidence\": ["

# ── 1. Recent commits ─────────────────────────────────────────────────────────
echo "  {\"source\": \"git\", \"type\": \"commits\", \"data\": "
git log --oneline -10 --no-decorate 2>/dev/null \
  | jq -R -s 'split("\n") | map(select(length > 0))'
echo "  },"

# ── 2. Health check ──────────────────────────────────────────────────────────
echo "  {\"source\": \"api\", \"type\": \"health\", \"data\": "
curl -sf "$BASE_URL/health" 2>/dev/null || echo '"unreachable"'
echo "  },"

# ── 3. Ready check ───────────────────────────────────────────────────────────
echo "  {\"source\": \"api\", \"type\": \"readiness\", \"data\": "
curl -sf "$BASE_URL/ready" 2>/dev/null || echo '"unreachable"'
echo "  },"

# ── 4. Agent list (registered agents) ─────────────────────────────────────────
echo "  {\"source\": \"api\", \"type\": \"agents\", \"data\": "
curl -sf "$BASE_URL/api/v1/agents" 2>/dev/null || echo '"unreachable"'
echo "  },"

# ── 5. Docker containers (if applicable) ──────────────────────────────────────
if command -v docker &>/dev/null; then
  echo "  {\"source\": \"docker\", \"type\": \"ps\", \"data\": "
  docker ps --format '{{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}' 2>/dev/null \
    | jq -R -s 'split("\n") | map(select(length > 0))'
  echo "  },"
fi

# ── 6. Recent deploy diff ────────────────────────────────────────────────────
echo "  {\"source\": \"git\", \"type\": \"diffstat\", \"data\": "
git log --oneline -1 --stat 2>/dev/null \
  | jq -R -s 'split("\n") | map(select(length > 0))'
echo "  }"

echo "]}"  # close evidence array
