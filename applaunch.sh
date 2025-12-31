#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="${SCRIPT_DIR}/apps/web"

echo "🎨 Starting frontend (Vite)..."
cd "${WEB_DIR}"

if [[ ! -d node_modules ]]; then
  echo "ℹ️  node_modules not found; running npm install..."
  npm install
fi

# Foreground so logs stream to this terminal
exec npm run dev -- --port 5173
