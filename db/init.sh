#!/bin/bash
# Initialize database: create schema and views

set -e

DB_NAME="omc_pipeline_poc"

echo "Creating database $DB_NAME (if it doesn't exist)..."
createdb $DB_NAME 2>/dev/null || echo "Database $DB_NAME already exists"

echo "Loading schema..."
psql $DB_NAME < "$(dirname "$0")/schema.sql"

echo "Loading views..."
psql $DB_NAME < "$(dirname "$0")/views.sql"

echo "Database initialized successfully!"
echo ""
echo "To load seed data, run:"
echo "  curl -X POST http://localhost:8000/api/import/seed -H 'Content-Type: application/json' -d '{}'"

