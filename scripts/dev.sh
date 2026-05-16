#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn nextusinger.main:app --reload --port 7860 &
BACKEND_PID=$!
cd "$ROOT/frontend"
npm install
npm run dev
kill $BACKEND_PID
