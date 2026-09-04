#!/usr/bin/env bash
# OSINTGraph — setup macOS / Linux
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "OSINTGraph setup"
command -v node >/dev/null || { echo "Node.js 20+ requis"; exit 1; }
command -v python3 >/dev/null || { echo "Python 3.11+ requis"; exit 1; }

npm install

cd backend
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -r requirements.txt

cd "$ROOT"
[[ -f backend/.env ]] || cp backend/.env.example backend/.env
mkdir -p data

echo ""
echo "Pret. Lancez :"
echo "  npm run dev           # React + API (http://localhost:5173)"
echo "  npm run dev:streamlit # Preview Streamlit (http://localhost:8501)"
