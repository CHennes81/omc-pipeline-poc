#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"

echo "🗄️  Starting Postgres (dev)"
echo "   Host: ${DB_HOST}"
echo "   Port: ${DB_PORT}"
echo

is_db_up() {
  nc -z "${DB_HOST}" "${DB_PORT}" >/dev/null 2>&1
}

wait_for_db() {
  local max_seconds="${1:-15}"
  local start_ts
  start_ts="$(date +%s)"

  while ! is_db_up; do
    local now_ts
    now_ts="$(date +%s)"
    local elapsed=$((now_ts - start_ts))
    if (( elapsed >= max_seconds )); then
      return 1
    fi
    sleep 1
  done
  return 0
}

if is_db_up; then
  echo "✅ Postgres already running on ${DB_HOST}:${DB_PORT}"
  exit 0
fi

echo "ℹ️  Postgres not reachable on ${DB_HOST}:${DB_PORT}"
echo

# Try Postgres.app first (most common on macOS)
if [[ -d "/Applications/Postgres.app" ]]; then
  echo "▶️  Attempting to start Postgres.app..."
  open -a "Postgres"
else
  echo "ℹ️  Postgres.app not found in /Applications"
fi

# If not up yet, try Homebrew service (best-effort; may fail if not installed)
if ! wait_for_db 5; then
  echo "▶️  Attempting to start Homebrew Postgres service (best-effort)..."
  # Note: adjust postgresql@16 to whatever you have installed, if needed.
  brew services start postgresql@16 >/dev/null 2>&1 || brew services start postgresql >/dev/null 2>&1 || true
fi

echo "⏳ Waiting for Postgres to accept connections..."
if wait_for_db 20; then
  echo "✅ Postgres is up on ${DB_HOST}:${DB_PORT}"
  exit 0
fi

echo
echo "❌ Postgres still not reachable on ${DB_HOST}:${DB_PORT}"
echo "   Next steps:"
echo "   1) If you use Postgres.app: open it and click 'Start'"
echo "   2) If you use Homebrew:    brew services list | grep postgres"
echo "   3) Verify port:            lsof -nP -iTCP:${DB_PORT} -sTCP:LISTEN"
exit 1
