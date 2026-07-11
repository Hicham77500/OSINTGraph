#!/usr/bin/env bash
# Security dependency audit for OSINTGraph
set -e
echo "=== Backend pip-audit ==="
cd "$(dirname "$0")/../backend"
if [ -d .venv ]; then
  .venv/bin/pip install pip-audit -q 2>/dev/null || true
  .venv/bin/pip-audit || echo "pip-audit: review output above"
else
  echo "No .venv found — skip pip-audit"
fi

echo ""
echo "=== Frontend npm audit ==="
cd "$(dirname "$0")/../frontend"
npm audit --audit-level=moderate || echo "npm audit: review output above"

echo ""
echo "Done. Document findings in docs/AUDIT-2026-07.md if needed."
