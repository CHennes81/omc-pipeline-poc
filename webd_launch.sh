#!/usr/bin/env bash
set -euo pipefail

# Web launch script (Vite) — DEV mode
# - Assumes this script lives in the project root
# - Forces Vite to use port 5173 (and fail if it's taken) for consistent CORS behavior

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="${SCRIPT_DIR}/apps/web"

WEB_HOST="127.0.0.1"
WEB_PORT="5173"

die() {
  echo "❌ $*" >&2
  exit 1
}

port_in_use() {
  local port="$1"
  lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
}

echo "🌐 Starting web (Vite, DEV)..."
cd "${WEB_DIR}"

command -v npm >/dev/null 2>&1 || die "npm not found (is Node installed and on PATH?)"

if port_in_use "${WEB_PORT}"; then
  echo "❌ Port ${WEB_PORT} is already in use. Stop the existing process first:" >&2
  lsof -nP -iTCP:"${WEB_PORT}" -sTCP:LISTEN >&2 || true
  exit 1
fi

exec npm run dev -- --host "${WEB_HOST}" --port "${WEB_PORT}" --strictPort
