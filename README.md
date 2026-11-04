# Production Lineage Concierge (POC)

A proof-of-concept web application demonstrating deterministic asset lineage and auditability for media production workflows, built on MovieLabs OMC concepts.

## Overview

This POC implements:

- Deterministic pipeline modeling (CAPTURE → OFFLOAD → DAILIES → EDIT_EXPORT → TURNOVER → ARCHIVE)
- Metadata-first lineage tracking with explicit `derivedFrom` relationships
- Evidence-based query system (Ask templates)
- Immutable event log for auditability

**Phase 1 Scope:**

- No AI/LLM calls
- No vector databases
- No real media processing (MP4s are stand-ins referenced by URIs)
- Deterministic behavior only

## Prerequisites

- **PostgreSQL** (running locally via Postgres.app or similar)
- **Python 3.x** (for backend)
- **Node.js** (for frontend)
- Database: `omc_pipeline_poc` (will be created automatically)

## Setup

### 1. Database Setup

Create the database and load schema:

```bash
# Create database (if it doesn't exist)
createdb omc_pipeline_poc

# Load schema
psql omc_pipeline_poc < db/schema.sql

# Load views
psql omc_pipeline_poc < db/views.sql
```

### 2. Backend Setup

```bash
cd apps/api

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, defaults work for local dev)
# DATABASE_URL=postgresql://localhost/omc_pipeline_poc
# CORS_ORIGINS=http://localhost:5173
# APP_ENV=local
#
# Natural-language Ask (optional). Requires ASK_NL_ENABLED=true and the selected provider's key:
# LLM_PROVIDER=anthropic          # anthropic (active) | openai (inactive; pip install -r requirements-openai.txt)
# LLM_MODEL=claude-haiku-5-5      # optional; e.g. claude-sonnet-5-5 for demos
# ANTHROPIC_API_KEY=sk-ant-...
```

The LLM is reached only through the provider-neutral layer in `apps/api/app/llm/`; to add a vendor,
implement `LLMProvider` in `app/llm/providers/` and register it in `app/llm/factory.py`.
Tests: `pip install -r requirements-dev.txt && python -m pytest` (from `apps/api`).

### 3. Frontend Setup

```bash
cd apps/web

# Install dependencies
npm install
```

## Running the Application

### Start Backend

```bash
cd apps/api
source venv/bin/activate  # If using venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### Start Frontend

```bash
cd apps/web
npm run dev
```

Frontend will be available at: http://localhost:5173

### Load Seed Data

After starting the backend, load the seed dataset:

```bash
curl -X POST http://localhost:8000/api/import/seed \
  -H "Content-Type: application/json" \
  -d '{"mode": null}'
```

Or use the reset mode to clear and reload:

```bash
curl -X POST http://localhost:8000/api/import/seed \
  -H "Content-Type: application/json" \
  -d '{"mode": "reset_and_seed"}'
```

## Usage

### Dashboard

Navigate to http://localhost:5173 to see:

- Shots by stage (counts)
- Blocked shots list
- All shots table

### Shot Detail

Click on any shot code to view:

- Versions grouped by type
- Lineage chain visualization
- Events timeline

### Packages

View packages and their members:

- Package list (TURNOVER, ARCHIVE, etc.)
- Package members (versions included)

### Ask

Query the system using deterministic templates:

- Select from supported questions or type your own
- View answers with evidence tables
- See explanation (template + parameters)

## API Endpoints

### Core Endpoints

- `GET /api/productions` - List all productions
- `GET /api/shots?production_code=EXFTR` - List shots with stage
- `GET /api/shots/{shot_code}?production_code=EXFTR` - Shot detail
- `GET /api/shots/{shot_code}/lineage?production_code=EXFTR` - Lineage chain
- `GET /api/shots/{shot_code}/events?production_code=EXFTR` - Events timeline
- `GET /api/packages?production_code=EXFTR` - List packages
- `GET /api/packages/{package_id}` - Package detail with members
- `POST /api/ask` - Ask a question (deterministic templates)

### Import/Seed

- `POST /api/import/seed` - Load seed data

### Health

- `GET /health` - Health check

## Example API Calls

```bash
# Get all shots
curl http://localhost:8000/api/shots?production_code=EXFTR

# Get shot detail
curl http://localhost:8000/api/shots/011_002?production_code=EXFTR

# Get lineage
curl http://localhost:8000/api/shots/011_002/lineage?production_code=EXFTR

# Ask a question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"production_code": "EXFTR", "question": "What is the latest camera original for shot 011_002?"}'
```

## Project Structure

```
omc-pipeline-poc/
├── apps/
│   ├── api/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py   # FastAPI app
│   │   │   ├── routes.py # API routes
│   │   │   ├── models.py # SQLAlchemy models
│   │   │   ├── schemas.py # Pydantic schemas
│   │   │   ├── ask_templates.py # Ask template implementations
│   │   │   └── seed.py   # Seed loading
│   │   └── requirements.txt
│   └── web/              # React frontend
│       └── src/
│           ├── pages/     # Page components
│           └── api/       # API client
├── db/
│   ├── schema.sql        # Database schema
│   ├── views.sql         # Database views
│   └── seed.sql          # Seed data
└── artifacts/            # Control documents
    ├── FuncTechSpec.md   # Functional spec
    ├── DevPlan.md        # Project plan
    └── ...
```

## Seed Dataset

The seed includes:

- 1 production (EXFTR)
- 5 shots (011_002, 011_022, 012_010, 012_011, 013_015)
- Complete lineage chains: CAMERA_ORIGINAL → HDE_MASTER → DAILIES_PROXY → (some) EDIT_EXPORT
- Blocked cases: shots with dailies but no edit export
- Packages: 1 TURNOVER package, 1 ARCHIVE package
- Events: Full event timeline per shot

## Development Notes

- **Deterministic only**: No probabilistic logic, no AI/LLM
- **Evidence-first**: All answers include supporting data rows
- **Immutable events**: Event log is append-only
- **Lineage via FK**: Explicit `derived_from_version_id` relationships

## Troubleshooting

### Database Connection Issues

Ensure PostgreSQL is running and the database exists:

```bash
psql -l | grep omc_pipeline_poc
```

### CORS Errors

Ensure `CORS_ORIGINS` in backend `.env` includes your frontend URL (default: http://localhost:5173)

### Seed Data Not Loading

Check backend logs for SQL errors. Ensure schema and views are loaded first.

## Next Steps (Phase 2 - Optional)

- Lineage graph visualization
- Read-only audit export
- Hosted deployment (Railway + Cloudflare Pages)
