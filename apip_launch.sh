#!/usr/bin/env bash
set -euo pipefail

# API launch script (FastAPI via Uvicorn) — PROD mode
# - Assumes this script lives in the project root
# - Uses the project-local venv at: ./apps/api/venv
# - Runs without auto-reload
# - Idempotent across terminal sessions: will overwrite mismatched env vars

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="${SCRIPT_DIR}/apps/api"
VENV_DIR="${API_DIR}/venv"

API_HOST="127.0.0.1"
API_PORT="8000"

PROD_WEB_PORT="4173"

DESIRED_APP_ENV="prod"
DESIRED_CORS_ORIGINS="http://localhost:${PROD_WEB_PORT},http://127.0.0.1:${PROD_WEB_PORT}"

die() {
  echo "❌ $*" >&2
  exit 1
}

port_in_use() {
  local port="$1"
  lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
}

set_env_if_needed() {
  local var_name="$1"
  local desired_value="$2"
  local current_value="${!var_name-}"

  if [[ "${current_value}" != "${desired_value}" ]]; then
    if [[ -n "${current_value}" ]]; then
      echo "ℹ️  ${var_name} was set to '${current_value}' — overwriting for PROD"
    else
      echo "ℹ️  ${var_name} not set — setting for PROD"
    fi
    export "${var_name}=${desired_value}"
  else
    echo "✅ ${var_name} already correct for PROD"
  fi
}

echo "🚀 Starting backend (FastAPI via uvicorn, PROD-mode)..."
cd "${API_DIR}"

[[ -d "${VENV_DIR}" ]] || die "Missing venv at: ${VENV_DIR} (create it first, then re-run)"
[[ -f "${VENV_DIR}/bin/activate" ]] || die "Missing venv activate script: ${VENV_DIR}/bin/activate"

if port_in_use "${API_PORT}"; then
  echo "❌ Port ${API_PORT} is already in use. Stop the existing process first:" >&2
  lsof -nP -iTCP:"${API_PORT}" -sTCP:LISTEN >&2 || true
  exit 1
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

export PYTHONPATH="${API_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

set_env_if_needed "APP_ENV" "${DESIRED_APP_ENV}"
set_env_if_needed "CORS_ORIGINS" "${DESIRED_CORS_ORIGINS}"

exec python -m uvicorn app.main:app --host "${API_HOST}" --port "${API_PORT}"
