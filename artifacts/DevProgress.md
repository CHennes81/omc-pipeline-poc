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
