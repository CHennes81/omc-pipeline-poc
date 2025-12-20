# DevProgress.md

## Project
MovieLabs OMC – Production Lineage Concierge (POC)

This document is an **append-only execution log**.
Entries are factual and chronological.

---

## 2025-12-19 – Control Docs Realignment
- Completely rewrote DevPlan.md for Production Lineage Concierge POC
- Completely rewrote DevProcess.md to define deterministic, Cursor-driven workflow
- Reset DevProgress.md for this repository
- Confirmed Phase 1 scope:
  - Deterministic pipeline modeling
  - No AI / no vector database
  - Metadata-first lineage and auditability

Status:
- Ready to begin Cursor CodeGen for Phase 1 (DB schema + seed)

---

## 2025-12-19 – Phase 1 End-to-End Implementation

Implemented complete Phase 1 skeleton for Production Lineage Concierge POC.

### Database Layer (db/)

**Files created:**
- `db/schema.sql` - Complete database schema with tables: productions, shots, assets, versions, version_lineage, packages, package_members, events
- `db/views.sql` - View `v_shot_stage` for deterministic stage computation based on event types
- `db/seed.sql` - Seed dataset with:
  - 1 production (EXFTR)
  - 5 shots (011_021, 011_022, 012_010, 012_011, 013_015)
  - Complete lineage chains: CAMERA_ORIGINAL → HDE_MASTER → DAILIES_PROXY → (some) EDIT_EXPORT
  - Blocked cases: 2 shots with dailies but no edit export
  - 1 TURNOVER package (3 shots), 1 ARCHIVE package (2 shots)
  - Full event timeline per shot
- `db/init.sh` - Database initialization script

**Key features:**
- UUID primary keys throughout
- JSONB columns for OMC-shaped payloads (versions.omc_json, events.details)
- Explicit lineage via `derived_from_version_id` FK
- Immutable event log (append-only)
- GIN indexes on JSONB columns

### Backend (apps/api/)

**Files created:**
- `apps/api/app/main.py` - FastAPI application with CORS middleware
- `apps/api/app/config.py` - Configuration management (database_url, cors_origins, app_env)
- `apps/api/app/database.py` - SQLAlchemy engine and session management
- `apps/api/app/models.py` - SQLAlchemy ORM models for all tables
- `apps/api/app/schemas.py` - Pydantic schemas for request/response models
- `apps/api/app/routes.py` - All API endpoints per FuncTechSpec Appendix A:
  - `POST /api/import/seed` - Load seed data
  - `GET /api/productions` - List productions
  - `GET /api/shots` - List shots with stage
  - `GET /api/shots/{shot_code}` - Shot detail
  - `GET /api/shots/{shot_code}/lineage` - Lineage chain
  - `GET /api/shots/{shot_code}/events` - Events timeline
  - `GET /api/assets/{asset_id}/versions` - Asset versions
  - `GET /api/versions/{version_id}/lineage` - Version lineage
  - `GET /api/packages` - List packages
  - `GET /api/packages/{package_id}` - Package detail
  - `GET /api/packages/{package_id}/members` - Package members
  - `POST /api/ask` - Ask questions (deterministic templates)
  - `POST /api/shots/{shot_code}/ops/*` - Advance operations (placeholders)
- `apps/api/app/ask_templates.py` - Deterministic Ask template implementations:
  - `latest_camera_original(shot_code)`
  - `lineage_chain_to_latest_edit_export(shot_code)`
  - `shots_with_dailies_no_edit_export()`
  - `shots_ready_for_turnover_and_missing()`
  - `package_members(package_id)`
  - `source_relink_keys(shot_code)`
  - `latest_versions_by_type(shot_code)`
  - `archive_status(production_code)`
  - Simple keyword-based question routing
- `apps/api/app/seed.py` - Seed data loading from SQL file
- `apps/api/requirements.txt` - Python dependencies (FastAPI, SQLAlchemy, psycopg2, pydantic)
- `apps/api/run.sh` - Server startup script

**Key features:**
- FastAPI with SQLAlchemy ORM
- Structured error responses per spec
- Deterministic queries only (no AI/LLM)
- Evidence-based Ask responses with supporting data rows
- CORS configured for local development

### Frontend (apps/web/)

**Files created:**
- `apps/web/src/api/client.ts` - API client with TypeScript interfaces
- `apps/web/src/pages/Dashboard.tsx` - Dashboard page:
  - Production selector
  - Shots by stage (counts table)
  - Blocked shots list
  - All shots table
- `apps/web/src/pages/ShotDetail.tsx` - Shot detail page:
  - Shot header (scene, description)
  - Versions grouped by type
  - Lineage chain visualization (simple vertical list)
  - Events timeline table
- `apps/web/src/pages/Packages.tsx` - Packages page:
  - Package list with selection
  - Package members table
- `apps/web/src/pages/Ask.tsx` - Ask page:
  - Supported question templates (click-to-fill)
  - Question input
  - Answer display
  - Evidence tables (dynamic columns)
  - Explanation block (template + params)
- `apps/web/src/App.tsx` - Updated with React Router navigation
- `apps/web/src/pages/index.ts` - Page exports

**Dependencies added:**
- `react-router-dom` for navigation

**Key features:**
- Evidence-first UI (tables, IDs, timestamps)
- Minimal CSS, no design system
- No auth, no complex state management
- API base URL from env (VITE_API_BASE_URL)

### Documentation

**Files created/updated:**
- `README.md` - Comprehensive setup and usage instructions:
  - Prerequisites
  - Database setup
  - Backend/frontend setup
  - Running instructions
  - API endpoint documentation
  - Example curl commands
  - Project structure
  - Troubleshooting

### Implementation Status

**Completed:**
- ✅ Database schema and views
- ✅ Seed data with complete lineage chains
- ✅ All API endpoints from FuncTechSpec Appendix A
- ✅ Deterministic Ask templates (8 of 12 specified templates)
- ✅ React frontend pages (Dashboard, Shot Detail, Packages, Ask)
- ✅ Navigation and routing
- ✅ README with run instructions

**Remaining (optional for Phase 1):**
- Full implementation of advance operations (`/ops/*` endpoints are placeholders)
- Remaining 4 Ask templates (relink_conflicts, dailies_transform_details, deliveries_to_vendor_last_n_days, highest_quality_source_for_reconform)
- Shot detail page: load versions via asset_id (currently stubbed)
- Better blocked shots detection (currently simplified)

**Known issues:**
- Shot detail page doesn't load versions yet (needs asset_id lookup)
- Advance operations are placeholders (need full state machine logic)
- Some Ask templates not yet implemented (4 of 12)

### Next Steps

1. Test end-to-end: start backend → load seed → browse dashboard → view shot detail → query Ask
2. Implement remaining Ask templates
3. Complete advance operations if time allows
4. Fix shot detail versions loading

**Files changed:** 30+ files created/modified
**Lines of code:** ~3000+ (backend + frontend + database)

---

## 2025-12-19 – SQLAlchemy 2.x Fixes and Health Endpoint

Fixed two runtime issues in the FastAPI backend.

### SQLAlchemy 2.x Execute Fix

**Issue:** `seed.load_seed_sql` was failing with "string is not executable" errors due to SQLAlchemy 2.x requiring explicit `text()` wrapper for raw SQL strings.

**Fix:** Updated `apps/api/app/seed.py`:
- Added `from sqlalchemy import text` import
- Wrapped all raw SQL strings with `text()`:
  - TRUNCATE statement (when reset=True)
  - Seed SQL file contents
  - COUNT query for shots_loaded

**Files changed:**
- `apps/api/app/seed.py` - Wrapped 3 SQL execute calls with `text()`

**Result:** `POST /api/import/seed` now executes successfully without SQLAlchemy 2.x errors.

### Health Endpoint Implementation

**Issue:** `/health` endpoint existed but returned extra fields beyond the required `{"status": "ok"}`.

**Fix:** Updated `apps/api/app/main.py`:
- Simplified `/health` endpoint to return exactly `{"status": "ok"}`
- Endpoint is mounted at app level (not under `/api` prefix), so final path is exactly `/health`

**Files changed:**
- `apps/api/app/main.py` - Simplified health check response

**Result:** `GET /health` returns 200 with `{"status": "ok"}` at exactly `/health` path.

---

## 2025-12-19 – Seed Data FK Integrity Fix

Fixed foreign key violation in seed data and performed full referential integrity validation.

### Problem

`POST /api/import/seed` was failing with:
```
psycopg2.errors.ForeignKeyViolation: insert/update on table "assets" violates FK constraint "assets_shot_id_fkey"
DETAIL: Key (shot_id)=(550e8400-e29b-41d4-a716-446655440000) is not present in table "shots".
```

**Root cause:** Asset row with id `550e8400-e29b-41d4-a716-446655440105` had `shot_id` incorrectly set to production UUID `550e8400-e29b-41d4-a716-446655440000` instead of a valid shot UUID.

### Fix

**Corrected row:** Asset `550e8400-e29b-41d4-a716-446655440105`
- **Before:** `shot_id = '550e8400-e29b-41d4-a716-446655440000'` (production UUID, wrong)
- **After:** `shot_id = '550e8400-e29b-41d4-a716-446655440005'` (shot 013_015, correct)

This asset now correctly references shot `550e8400-e29b-41d4-a716-446655440005` (shot_code: 013_015), maintaining the "one asset per shot" pattern.

### Full Integrity Validation

Performed systematic review of all FK relationships in seed data:

**Validated relationships:**
- ✅ shots → productions (5 shots, all reference production 0000)
- ✅ assets → shots (5 assets, all reference valid shots 0001-0005)
- ✅ assets → productions (5 assets, all reference production 0000)
- ✅ versions → assets (18 versions, all reference valid assets 0101-0105)
- ✅ versions → versions (derived_from: 13 references, all valid)
- ✅ version_lineage → versions (13 edges, all derived/source references valid)
- ✅ events → shots (18 events, all reference valid shots)
- ✅ events → versions (18 events with version_id, all valid)
- ✅ events → packages (5 events with package_id, all valid)
- ✅ packages → productions (2 packages, both reference production 0000)
- ✅ package_members → packages (5 members, all reference valid packages)
- ✅ package_members → versions (5 members, all reference valid versions)

**No other integrity issues found.** All FK relationships are valid.

### Verification Queries

Added verification queries for manual integrity checking:
- `db/seed_verify.sql` - Standalone verification script with:
  - Expected count queries for all tables
  - FK integrity checks (should return 0 violations)
- Comments in `db/seed.sql` - Inline verification queries as comments

**Files changed:**
- `db/seed.sql` - Fixed asset 0105 shot_id FK reference
- `db/seed_verify.sql` - New verification script with count and FK checks

**Result:** `POST /api/import/seed` now executes successfully without FK violations. All referential integrity confirmed.

---

## 2025-12-19 – Frontend Import Fix and npm Install Fix

Fixed two issues preventing the frontend from running and npm install from completing.

### Dashboard Import Error Fix

**Problem:** Frontend showed blank white page with browser console error:
```
Uncaught SyntaxError: The requested module '/src/api/client.ts' does not provide an export named 'Production'
```

**Root cause:** TypeScript types (interfaces) were being imported as runtime values. With `verbatimModuleSyntax: true` in tsconfig, type-only imports must use `import type` syntax to prevent runtime module resolution errors.

**Fix:** Updated all page components to use `import type` for type-only imports:
- `apps/web/src/pages/Dashboard.tsx` - Separated `api` (value) from `Production, ShotSummary` (types)
- `apps/web/src/pages/ShotDetail.tsx` - Separated `api` from `ShotDetail, Version, Event, LineageNode`
- `apps/web/src/pages/Packages.tsx` - Separated `api` from `Package`
- `apps/web/src/pages/Ask.tsx` - Separated `api` from `AskResponse`

**Files changed:**
- `apps/web/src/pages/Dashboard.tsx` - Fixed type imports
- `apps/web/src/pages/ShotDetail.tsx` - Fixed type imports
- `apps/web/src/pages/Packages.tsx` - Fixed type imports
- `apps/web/src/pages/Ask.tsx` - Fixed type imports

**Result:** Frontend now loads without console errors. Dashboard and all pages render correctly.

### npm Install Husky Fix

**Problem:** `npm install` failed with:
```
sh: husky: command not found
```

**Root cause:** `prepare` script runs `husky` before husky is installed, causing install to fail.

**Fix:** Updated root `package.json` prepare script to tolerate husky not being available:
- Changed `"prepare": "husky"` to `"prepare": "husky || true"`

**Files changed:**
- `package.json` - Made prepare script non-blocking

**Result:** `npm install` now completes successfully even if husky isn't available yet.

### How to Verify

```bash
# 1. Clean install (from repo root)
npm install
# Should complete without errors

# 2. Start frontend dev server
cd apps/web
npm run dev

# 3. Open browser to http://localhost:5173
# Should see Dashboard (not blank white page)
# No console errors
```

**Files changed:**
- `apps/web/src/pages/Dashboard.tsx` - Fixed type imports
- `apps/web/src/pages/ShotDetail.tsx` - Fixed type imports
- `apps/web/src/pages/Packages.tsx` - Fixed type imports
- `apps/web/src/pages/Ask.tsx` - Fixed type imports
- `package.json` - Made husky prepare script non-blocking

**Result:** Frontend loads correctly and npm install works reliably.
