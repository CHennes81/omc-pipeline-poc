#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="${SCRIPT_DIR}/apps/api"
VENV_DIR="${API_DIR}/venv"

echo "🔧 Starting backend (FastAPI via uvicorn)..."
cd "${API_DIR}"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "❌ Missing venv at: ${VENV_DIR}"
  echo "   Create it first, then re-run."
  exit 1
fi

# Activate venv
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Ensure 'app' package resolves (fixes: ModuleNotFoundError: No module named 'app')
export PYTHONPATH="${API_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

# Foreground so logs stream to this terminal
exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
