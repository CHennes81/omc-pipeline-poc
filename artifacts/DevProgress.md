# DevProgress.md

## Project

MovieLabs OMC – Production Lineage Concierge (POC)

This document is an **append-only execution log**.
Entries are factual and chronological.

---

## Phase A – Metadata Inspector v1 (Read-only)

**Goal:** Read-only inspector for version JSON metadata; OMC compliance deferred.

**Checklist:**

- [x] API: return Version.omc_json + Version.creative_context in GET /assets/{asset_id}/versions
- [x] API schema: VersionResponse includes omc_json + creative_context (optional)
- [x] UI: add global Inspector Drawer (right-side slide-over)
- [x] UI: add header toggle affordance on detail pages (Shot Detail, Packages)
- [x] UI: implement Overview tab (lightweight, curated; hides null/empty; nested objects shown as [object])
- [x] UI: implement Raw tab (pretty-printed JSON dump of full payload)
- [x] Optional: Copy JSON button on Raw (copies exactly displayed string)
- [x] Smoke test: confirm metadata fields appear in API response + Inspector Raw view

**Implementation summary (2026-02-13):**

**Files changed:**

- `apps/api/app/schemas.py` – Added `omc_json` and `creative_context` (Optional[Dict[str, Any]]) to `VersionResponse`
- `apps/api/app/routes.py` – Added `omc_json` and `creative_context` to `get_asset_versions` return dict; added `get_shot_versions` endpoint (GET /shots/{shot_code}/versions)
- `apps/web/src/api/client.ts` – Added `omc_json` and `creative_context` to Version interface; added `getShotVersions` and `getAssetVersions`
- `apps/web/src/context/InspectorContext.tsx` – **New.** Inspector state (open, payload)
- `apps/web/src/components/InspectorDrawer.tsx` – **New.** Drawer with Overview + Raw tabs, Copy button
- `apps/web/src/components/InspectorDrawer.css` – **New.** Drawer styles
- `apps/web/src/App.tsx` – Wrapped app in `InspectorProvider`, rendered `InspectorDrawer`
- `apps/web/src/pages/ShotDetail.tsx` – Load versions via `getShotVersions`; Inspect button; click version row to inspect
- `apps/web/src/pages/Packages.tsx` – Inspect button; inspect selected package with members

**How to test manually:**

1. Start API and web app; load seed data (POST /api/import/seed with mode: "reset_and_seed")
2. Navigate to Shot Detail (e.g. /shot/011_001). Click a version row – Inspector opens with that Version. Raw tab shows `omc_json` and `creative_context` when present.
3. Or: GET /api/shots/011_001/versions?production_code=EXFTR – response includes `omc_json` and `creative_context` fields per Version.

**Limitations / deferrals:**

- Inspector not wired on Dashboard, All Shots, or Ask pages
- Payload clears when navigating away; open state (drawer visible) persists
- OMC compliance validation deferred to later phase

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

**Root cause:** `prepare` script runs `husky` before husky is installed, causing install to fail. Additionally, in npm workspaces, `husky` may not be in PATH, requiring `npm exec` to locate it.

**Fix:** Updated root `package.json` prepare script to use `npm exec` and tolerate husky not being available:

- Changed `"prepare": "husky || true"` to `"prepare": "npm exec -- husky install || true"`
- This ensures husky is found via npm's package resolution (works in workspaces)
- The `|| true` ensures install doesn't fail if husky isn't available yet
- `.husky/` directory already exists with hooks (pre-commit, commit-msg), so `husky install` will properly link them

**Files changed:**

- `package.json` - Updated prepare script to use `npm exec -- husky install`

**Result:** `npm install` now completes successfully. Husky hooks are properly initialized via npm exec, avoiding PATH dependency issues in workspaces.

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

---

## 2025-12-22 – Lineage Endpoint SQL Syntax Fix

Fixed HTTP 500 error in `GET /api/shots/{shot_code}/lineage` endpoint caused by invalid PostgreSQL syntax in recursive CTE.

### Problem

**Error:** `GET /api/shots/{shot_code}/lineage?production_code=EXFTR` returned HTTP 500 with:

```
psycopg2.errors.SyntaxError: syntax error at or near "UNION" (LINE 11: UNION ALL)
```

**Root cause:** The `WITH RECURSIVE` CTE had `ORDER BY ... LIMIT 1` in the anchor SELECT immediately before `UNION ALL`, which PostgreSQL rejects. In recursive CTEs, the anchor SELECT cannot have `ORDER BY`/`LIMIT` directly before `UNION ALL`.

### Fix

**Implementation:** Used approach B (subquery wrapper) to fix the SQL syntax:

- Wrapped the anchor query in a subquery: `FROM (SELECT ... ORDER BY ... LIMIT 1) v`
- This allows `ORDER BY`/`LIMIT` in the subquery while keeping the recursive CTE syntax valid
- Added cycle protection: `WHERE lc.depth < 20` to prevent infinite loops
- Fixed ordering: Changed `ORDER BY depth DESC` to `ORDER BY depth ASC` so latest version (depth 0) appears first
- Added tiebreaker: `ORDER BY v.created_at DESC, v.id DESC` to reliably select the latest version when timestamps are identical

**Query behavior:**

- Starts from the latest version (by `created_at DESC, id DESC`)
- Recursively follows `derived_from_version_id` backward to ancestors
- Returns chain ordered from latest to earliest (EDIT_EXPORT → CAMERA_ORIGINAL)
- Max depth of 20 prevents infinite recursion from cycles

**Files changed:**

- `apps/api/app/routes.py` - Fixed `get_shot_lineage` SQL query syntax and ordering

**Result:** Endpoint now returns HTTP 200 with correct lineage chain:

```json
{
  "shot_code": "011_021",
  "chain": [
    { "version_id": "...", "version_type": "EDIT_EXPORT", "derived_from": "..." },
    { "version_id": "...", "version_type": "DAILIES_PROXY", "derived_from": "..." },
    { "version_id": "...", "version_type": "HDE_MASTER", "derived_from": "..." },
    { "version_id": "...", "version_type": "CAMERA_ORIGINAL", "derived_from": null }
  ]
}
```

### How to Verify

```bash
# 1. Ensure API is running and seed is loaded
curl -X POST http://127.0.0.1:8000/api/import/seed -H "Content-Type: application/json" -d '{"mode":"reset_and_seed"}'

# 2. Test lineage endpoint
curl "http://127.0.0.1:8000/api/shots/011_021/lineage?production_code=EXFTR"
# Should return HTTP 200 with valid JSON chain
```

---

## 2026-01-12 – Natural Language Ask Routing Implementation (Appendix G)

Implemented complete Natural Language Ask routing system per FuncTechSpec Appendix G requirements.

### Summary

This implementation adds LLM-based intent routing to the Ask system while preserving strict deterministic execution. The system routes natural language questions to predefined intents, extracts parameters, and enforces confidence gating with optional clarification loops. All execution remains deterministic via SQL templates (Phase 1).

### Backend Components

**Files created:**

- `apps/api/app/intent_registry.json` - Canonical intent registry (v0) with 8 intents:
  - `latest_camera_original`
  - `lineage_chain_to_latest_edit_export`
  - `shots_with_dailies_no_edit_export`
  - `shots_ready_for_turnover_and_missing`
  - `package_members`
  - `source_relink_keys`
  - `latest_versions_by_type`
  - `archive_status`
  - Each intent defines: intent_id, title, description, required/optional params with validation patterns, execution binding (sql_template)
  - Registry is Git-versioned and loaded at startup

- `apps/api/app/ask_executor.py` - AskExecutor interface and SqlTemplateExecutor implementation:
  - `AskExecutor` protocol defines `execute(intent_id, params)` interface
  - `SqlTemplateExecutor` implements Phase 1 execution via existing SQL templates
  - Decouples routing from execution (future: stored procedures)
  - Validates intent_id and ensures production_code is present

- `apps/api/app/nl_router.py` - NL routing with LLM integration:
  - `IntentRegistry` class loads and validates intent registry JSON
  - `NLRouter` class implements LLM-based intent resolution using OpenAI GPT-4o-mini
  - Routing logic:
    - Builds prompt with intent allowlist and parameter schemas
    - Calls LLM with strict JSON output format
    - Validates LLM response schema and intent_id
    - Validates extracted parameters against intent schema (type, pattern)
  - Confidence gating per Appendix G:
    - confidence >= ASK_NL_CONFIDENCE_MIN (0.80) + no ambiguity + all required params → OK
    - confidence >= ASK_NL_CONFIDENCE_CLARIFY_MIN (0.60) + first attempt + potentially resolvable → NEEDS_CLARIFICATION
    - else → UNANSWERABLE
    - Second attempt MUST resolve to OK or UNANSWERABLE (no further clarification)
  - `RoutingStatus` enum: OK, NEEDS_CLARIFICATION, UNANSWERABLE, ERROR
  - `RoutingResult` dataclass captures routing outcome with confidence, params, missing_params, ambiguity, user_message

**Files modified:**

- `apps/api/requirements.txt` - Added `openai==1.54.0` dependency

- `apps/api/app/config.py` - Added NL Ask ENVVARs per Appendix G:
  - `openai_api_key` (Optional[str], default None) - OpenAI API key (MUST NOT be committed)
  - `ask_nl_enabled` (bool, default False) - Master NL feature flag
  - `ask_dual_mode_ui` (bool, default False) - Show mode switcher in UI
  - `ask_default_mode` (str, default "deterministic") - Initial mode on page load
  - `ask_nl_confidence_min` (float, default 0.80) - Min confidence for execution
  - `ask_nl_confidence_clarify_min` (float, default 0.60) - Min confidence for clarification
  - `is_nl_enabled()` method checks both flag and API key presence
  - Production-safe defaults: all NL features disabled by default

- `apps/api/app/schemas.py` - Added NL request/response types:
  - `AskRequest` extended with:
    - `mode` (Optional[str], default "deterministic") - "deterministic" or "nl"
    - `clarification_context` (Optional[Dict]) - For second-pass clarification
  - `AskClarificationResponse` schema for clarification responses:
    - `status` = "needs_clarification"
    - `user_message` (str) - Human-readable clarification question
    - `intent_id`, `confidence`, `missing_params` (optional metadata)

- `apps/api/app/routes.py` - Updated Ask endpoint for dual-mode operation:
  - Added `GET /api/config/ask` endpoint to expose NL config to frontend
  - `POST /api/ask` now supports both modes via `request.mode` parameter
  - Mode validation: rejects NL requests if `ASK_NL_ENABLED=false` or API key missing
  - Split handling into `_handle_deterministic_ask()` and `_handle_nl_ask()`
  - NL path:
    - Gets NLRouter instance (lazily initialized with OpenAI client)
    - Builds session context with production_code
    - Calls `router.route()` with clarification tracking
    - Handles routing outcomes:
      - OK → execute via AskExecutor
      - NEEDS_CLARIFICATION → return AskClarificationResponse
      - UNANSWERABLE → HTTP 400 error
      - ERROR → HTTP 500 error
  - Enhanced logging:
    - `_log_ask_failure()` extended with `mode` parameter
    - `_log_nl_routing()` logs all NL routing attempts with confidence, status, intent_id
  - Error handling preserves Appendix E semantics (no raw errors to users)

### Frontend Components

**Files modified:**

- `apps/web/src/api/client.ts` - Updated API client:
  - Added `AskClarificationResponse` interface
  - Added `AskConfig` interface for config endpoint
  - Updated `askQuestion()` to accept `mode` and `clarificationContext` parameters
  - Added `getAskConfig()` method to fetch NL availability

- `apps/web/src/pages/Ask.tsx` - Updated Ask page for NL mode:
  - Loads Ask config on mount via `useEffect(() => api.getAskConfig())`
  - State management:
    - `currentMode` tracks "deterministic" | "nl"
    - `clarification` stores clarification response if present
    - `clarificationContext` tracks state for second-pass clarification
  - Mode switcher (only visible if `dual_mode_ui=true` and `nl_enabled=true`):
    - Toggle between deterministic and NL modes
    - Shows "beta" badge for NL mode
    - Clears previous results when switching modes
  - `handleAsk()` updated:
    - Passes mode and clarificationContext to API
    - Detects clarification response and updates UI
    - Clears clarification state on successful execution
  - Clarification UI:
    - Displays `user_message` in highlighted box
    - Shows confidence percentage if available
    - Prompts user to provide clarification and re-submit
    - Indicates clarification mode with visual feedback
  - Question placeholder text adapts to mode
  - Supported Questions → Sample Questions in NL mode

### Architecture Compliance (Appendix G Guarantees)

**Deterministic Execution:**

- NL layer ONLY performs intent selection and parameter extraction
- All query execution uses existing SQL templates via AskExecutor
- No dynamic SQL generation
- No hallucinated joins or invented data

**Bounded Capability:**

- System can only answer questions mapped to Intent Registry
- Unsupported questions are rejected as "unanswerable"
- No guessing or invented parameters

**Explainable Routing:**

- All responses include `intent_id` (when applicable)
- Validated parameters are logged
- Confidence values are tracked and logged
- Routing outcomes are deterministic (ok / needs_clarification / unanswerable / error)

**Clarification Loop:**

- Maximum one clarification cycle per user request
- First attempt can return NEEDS_CLARIFICATION
- Second attempt MUST resolve to OK or UNANSWERABLE
- No conversational loops or retry-until-success behavior

**Production-Safe Defaults:**

- Missing or invalid ENVVARs → NL disabled, deterministic mode only
- OpenAI API key MUST be in ENVVAR (never committed)
- Dual-mode UI hidden unless explicitly enabled
- Default mode is deterministic (safe)

**Error Handling:**

- User-facing errors follow Appendix E semantics
- No raw HTTP status codes or stack traces in UI
- Structured logging to stdout for observability
- LLM schema violations → unanswerable (no retries)

### Phase 1 Scope

This implementation completes Phase 1 requirements:

- SQL template execution only (no stored procedures yet)
- No RAG or embeddings (static registry load)
- No dynamic intent retrieval (future: `IntentRetriever` abstraction)
- No multi-input transforms (single-intent routing only)

### Future Hooks (Explicit TODOs per Appendix G)

The following abstractions are in place for future phases:

- `AskExecutor` interface → ready for `StoredProcedureExecutor` implementation
- `IntentRegistry` → ready for RAG-based `IntentRetriever` (retrieve top-K intents instead of loading all)
- Confidence thresholds are configurable via ENVVARs (tunable in production)

### Files Changed Summary

**Backend (7 files):**

- `apps/api/requirements.txt` - Added openai dependency
- `apps/api/app/config.py` - Added 6 NL ENVVARs
- `apps/api/app/schemas.py` - Added AskClarificationResponse
- `apps/api/app/intent_registry.json` - NEW (Intent Registry v0)
- `apps/api/app/ask_executor.py` - NEW (AskExecutor + SqlTemplateExecutor)
- `apps/api/app/nl_router.py` - NEW (NLRouter + IntentRegistry + confidence gating)
- `apps/api/app/routes.py` - Updated /ask endpoint for dual-mode operation, added /config/ask

**Frontend (2 files):**

- `apps/web/src/api/client.ts` - Added NL types and API methods
- `apps/web/src/pages/Ask.tsx` - Added mode switcher and clarification UI

### Testing Notes

To enable NL mode:

```bash
# Set environment variables in .env or shell
export OPENAI_API_KEY="sk-..."
export ASK_NL_ENABLED=true
export ASK_DUAL_MODE_UI=true
export ASK_DEFAULT_MODE=deterministic  # or "nl"
export ASK_NL_CONFIDENCE_MIN=0.80
export ASK_NL_CONFIDENCE_CLARIFY_MIN=0.60

# Restart API server
cd apps/api
./run.sh
```

UI will show mode switcher when dual_mode_ui=true. Users can toggle between deterministic (safe, keyword-based) and NL (LLM-based) modes.

### Known Limitations (Phase 1)

- LLM calls have latency (~1-3 seconds per routing attempt)
- Confidence thresholds may require tuning based on real usage
- Intent Registry is static (no RAG retrieval yet)
- Only 8 intents supported (matches existing templates)
- No batch or multi-turn conversations (single question at a time)

### Compliance Checklist

- ✅ Implements all Appendix G required components
- ✅ Preserves Appendix E error handling semantics
- ✅ Follows CodingStandards.md (type hints, PEP 8, explicit over clever)
- ✅ Follows CommitGuide.md conventions (will commit with appropriate message)
- ✅ No linter errors in modified files
- ✅ Production-safe defaults (NL disabled unless explicitly enabled)
- ✅ Deterministic execution (no dynamic SQL)
- ✅ Explainable routing (intent_id + confidence + params logged)
- ✅ Clarification loop enforced (max 1 follow-up)
- ✅ No invented data or parameters

### Result

The system now supports both deterministic (keyword-based) and natural language (LLM-based) Ask modes. NL mode routes questions to intents using GPT-4o-mini, extracts parameters, enforces confidence gates, and optionally asks for clarification. All execution remains deterministic via SQL templates. The implementation is fully compliant with Appendix G requirements and preserves the system's core deterministic guarantees.

---

## 2026-01-12 – NL Trace Logging for Diagnostics

Added optional NL trace logging for intent selection and clarification diagnostics.

### Changes

**Backend (2 files):**

- `apps/api/app/config.py` - Added `ask_nl_trace: bool` setting (default: False)
- `apps/api/app/nl_router.py` - Added structured JSON trace logging at 6 pipeline stages:
  1. `nl_request_received` - Logs incoming question, clarification flag, production context
  2. `nl_registry_loaded` - Logs registry version and candidate intents
  3. `nl_prompt_built` - Logs model, temperature, prompt preview (1200 chars), full prompt hash
  4. `nl_openai_raw_response` - Logs raw LLM response preview (1200 chars)
  5. `nl_openai_parsed` - Logs extracted intent_id, confidence, missing_params, user_message
  6. `nl_decision` - Logs routing decision, reason, thresholds applied

### Implementation Notes

- Each NL request generates a unique `trace_id` (uuid4) reused across all log lines
- Logs are emitted as structured JSON to standard logging (console)
- Long content (prompts, responses) is truncated to 1200 characters with hash for verification
- No changes to routing logic, thresholds, or Appendix G semantics
- API key is never logged; all other data may be logged when trace is enabled
- No performance impact when `ASK_NL_TRACE=false` (default)

### Usage

To enable trace logging:

```bash
export ASK_NL_TRACE=true
```

Trace logs will show every handoff in the NL pipeline, making it possible to diagnose why clarification is or isn't triggering, observe confidence scores at each stage, and verify prompt construction.

---

## 2026-01-12 – Demo-Safe Backend Error Catching for /api/ask

Implemented global error catching for `/api/ask` endpoint to ensure demo-safe behavior per requirements.

### Changes

**Backend (1 file):**

- `apps/api/app/routes.py` - Added outermost catch-all try/except around entire `/api/ask` handler:
  - Error taxonomy: Three user-facing categories (constants):
    - `ASK_ERROR_CATEGORY_UNANSWERABLE` → "This question can't be answered..."
    - `ASK_ERROR_CATEGORY_DATA_RETRIEVAL_FAILURE` → "Unable to retrieve data..."
    - `ASK_ERROR_CATEGORY_REMOTE_SERVICES_UNAVAILABLE` → "Remote services unavailable..."
  - Exception mapping:
    - `ConnectionError`, `TimeoutError`, `OSError` → `remote_services_unavailable` (treats OpenAI failures as opaque external dependency)
    - `SQLAlchemyError`, `ValueError`, `KeyError` → `data_retrieval_failure`
    - All other exceptions → `data_retrieval_failure` (catch-all)
  - Consistent JSON error envelope on all failures (no raw exception text to client)
  - Updated `_log_ask_failure()` to include `intent_id` parameter and conditionally include stack traces (dev/local only)
  - Updated all inner handlers (`_handle_deterministic_ask`, `_handle_nl_ask`) to use new error taxonomy constants

### Implementation Notes

- Outermost catch-all prevents any uncaught exceptions from reaching client
- All error responses use user-facing messages (no raw exception text)
- Stack traces only logged in dev/local environments (`settings.app_env in ("local", "dev")`)
- Structured JSON logging includes: timestamp, env, endpoint, production_code, question, template/intent_id, error_code, error_category, exception message, stack trace (conditional)
- Routing semantics unchanged (no retries, no behavior changes)
- OpenAI SDK exceptions treated as opaque external dependency failures (caught by generic Exception handler)

### Verification

To verify locally:

```bash
# 1. Start API server
cd apps/api
./run.sh

# 2. Test error handling with invalid question (should return unanswerable)
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"production_code": "EXFTR", "question": "invalid question that cannot be routed"}'
# Expected: HTTP 400 with category "unanswerable"

# 3. Test with database error (simulate by stopping DB)
# Expected: HTTP 500 with category "data_retrieval_failure"

# 4. Check logs (should see structured JSON logs to stdout)
# In local/dev: includes stack_trace
# In prod: no stack_trace
```

**Files changed:**

- `apps/api/app/routes.py` - Added error taxonomy, outermost catch-all, updated logging

---

## 2026-01-12 – Improved Ask Error Handling Observability and Context Propagation

Enhanced error handling in `/api/ask` to improve observability and ensure context (template_name/intent_id) is available in logs when failures occur.

### Changes

**Backend (1 file):**

- `apps/api/app/routes.py`:
  - **Context propagation**: Added shared mutable `context` dict passed to inner handlers to track `template_name` and `intent_id` as they are resolved
  - **Outer catch logging**: Updated outer catch-all to use `context.get("template_name")` and `context.get("intent_id")` for more accurate error logs
  - **\_handle_deterministic_ask**:
    - Now accepts `context` parameter
    - Updates `context["template_name"]` when template is resolved
    - Wrapped `template_func(db, **params)` execution in try/except to catch SQL/template exceptions with proper context
    - Maps SQLAlchemyError/ValueError/KeyError → `data_retrieval_failure`
    - Maps other exceptions → `data_retrieval_failure` (catch-all)
  - **\_handle_nl_ask**:
    - Now accepts `context` parameter
    - Updates `context["intent_id"]` when intent is resolved (OK status)
    - Wrapped `router.route()` in try/except to catch connection/timeout errors → `remote_services_unavailable`
    - Wrapped `executor.execute()` in try/except to catch DB/template errors → `data_retrieval_failure`
    - Maps unexpected execution errors → `data_retrieval_failure` (catch-all)

### Implementation Notes

- Double-layer try/except pattern: inner handlers handle common failures with proper context, outer catch-all handles truly unexpected exceptions
- Context dict is minimal (only template_name and intent_id) and passed by reference
- Inner handlers log errors with resolved template_name/intent_id before raising HTTPException
- Outer catch-all uses context for logging when inner handlers don't catch exceptions
- No changes to routing semantics, confidence thresholds, clarification behavior, or response schemas
- No retries, backoff, or vendor-specific exception taxonomy

### Verification

To verify locally:

```bash
# 1. Start API server
cd apps/api
./run.sh

# 2. Test deterministic mode with template execution error
# (Simulate by temporarily breaking a template function)
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"production_code": "EXFTR", "question": "latest camera original for shot 011_021"}'
# Expected: Error log should include template_name="latest_camera_original"

# 3. Test NL mode with connection error (simulate by setting invalid OpenAI API key)
export OPENAI_API_KEY="invalid"
export ASK_NL_ENABLED=true
# Restart API, then:
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"production_code": "EXFTR", "question": "latest camera original for shot 011_021", "mode": "nl"}'
# Expected: Error log should include category="remote_services_unavailable"

# 4. Test NL mode with execution error (simulate DB error)
# Expected: Error log should include intent_id when available

# 5. Check logs - verify template_name/intent_id appear in error logs when failures occur
```

**Files changed:**

- `apps/api/app/routes.py` - Added context propagation, inner error handling with proper context

---

## 2026-01-12 – Fixed NameError for Ask Error Taxonomy Constants

Fixed runtime crash caused by undefined error taxonomy constants in `/api/ask` endpoint.

### Problem

`NameError: ASK_ERROR_CATEGORY_DATA_RETRIEVAL_FAILURE is not defined` occurred in `_handle_nl_ask` and outer catch-all, causing Ask UI to hang on "Thinking..." because the API never returned a response.

### Solution

**Backend (1 file):**

- `apps/api/app/routes.py` - Added error taxonomy constants at module scope:
  - `ASK_ERROR_CATEGORY_UNANSWERABLE = "unanswerable"`
  - `ASK_ERROR_CATEGORY_DATA_RETRIEVAL_FAILURE = "data_retrieval_failure"`
  - `ASK_ERROR_CATEGORY_REMOTE_SERVICES_UNAVAILABLE = "remote_services_unavailable"`
  - `ASK_USER_MESSAGES` dict mapping categories to user-facing messages

### Implementation Notes

- Constants defined at module level (after router initialization) for consistent access
- All 13 references to error categories now use the defined constants
- Behavior unchanged: same three user-facing categories and same error envelope shape
- No changes to routing semantics or exception handling logic

### Verification

To verify the fix:

```bash
# 1. Start API server
cd apps/api
./run.sh

# 2. Test NL mode with Wi-Fi off (simulates connection error)
# Disable network, then:
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"production_code": "EXFTR", "question": "latest camera original for shot 011_021", "mode": "nl"}'
# Expected: HTTP 503 with category "remote_services_unavailable" (not crash)

# 3. Test with forced internal error (simulate by temporarily breaking a template)
# Expected: HTTP 500 with category "data_retrieval_failure" (not crash)

# 4. Verify API returns proper error envelope in all cases
# All errors should return JSON with: code, message (user-facing), category
```

**Files changed:**

- `apps/api/app/routes.py` - Added error taxonomy constants at module scope

---

## 2026-01-12 – Added Application-Level Hard Timeout for NL Routing LLM Calls

Implemented 12-second application-level hard timeout on Natural Language routing LLM calls to prevent hanging when network connectivity is lost. Uses `anyio.fail_after()` as a provider-agnostic timeout guard in addition to OpenAI SDK timeout.

### Changes

**Backend (2 files):**

- `apps/api/app/nl_router.py`:
  - Added module constant `LLM_TIMEOUT_SECONDS = 12.0`
  - Wrapped LLM call with `anyio.fail_after(LLM_TIMEOUT_SECONDS)` for application-level timeout guard
  - Uses `anyio.to_thread.run_sync()` to run synchronous OpenAI call in thread with timeout enforcement
  - Added exception handling for `anyio.TooSlowError` (timeout exception from anyio.fail_after)
  - Kept existing OpenAI client `timeout=12.0` parameter (belt + suspenders approach)
  - Returns `RoutingResult` with `error_code="llm_timeout"` when timeout occurs
- `apps/api/app/routes.py`:
  - Updated ERROR status handling in `_handle_nl_ask` to map `llm_timeout` errors to `remote_services_unavailable`
  - Timeout errors return HTTP 503 (Service Unavailable) instead of HTTP 500
  - Other routing errors continue to map to `data_retrieval_failure` with HTTP 500

### Implementation Notes

- Timeout value: **12 seconds** (application-level hard limit via `anyio.fail_after()`)
- Provider-agnostic timeout guard using `anyio` (works regardless of OpenAI SDK behavior)
- Belt + suspenders: both OpenAI SDK timeout and application-level timeout
- Timeout exceptions (`TimeoutError`) are caught and mapped to `error_code="llm_timeout"`
- Timeout errors are mapped to `ASK_ERROR_CATEGORY_REMOTE_SERVICES_UNAVAILABLE` category
- HTTP status: 503 (Service Unavailable) for timeouts
- No retries, backoff, or vendor-specific exception taxonomy
- Existing routing semantics, confidence gating, and clarification behavior unchanged

### Verification

To verify the timeout:

```bash
# 1. Start API server
cd apps/api
./run.sh

# 2. Test with Wi-Fi off (simulates network timeout)
# Disable network connectivity, then:
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"production_code": "EXFTR", "question": "latest camera original for shot 011_021", "mode": "nl"}'
# Expected: Request completes within ~12 seconds (not hanging indefinitely)
# Expected: HTTP 503 with category "remote_services_unavailable"
# Expected: Error log includes error_code="llm_timeout"

# 3. Verify timeout is enforced (should not exceed 12 seconds)
# Use a network throttling tool or simulate slow connection
# Expected: Request fails with timeout after 12 seconds maximum
```

**Files changed:**

- `apps/api/app/nl_router.py` - Added timeout and exception handling
- `apps/api/app/routes.py` - Updated error mapping for timeouts

---

## 2026-01-12 – Fixed anyio Timeout Guard Implementation

Fixed TypeError and AttributeError in anyio timeout guard implementation.

### Problem

- `TypeError: '_GeneratorContextManager' object does not support the asynchronous context manager protocol` - `anyio.fail_after()` was used with `async with` but it's a sync context manager
- `AttributeError: module 'anyio' has no attribute 'TooSlowError'` - Non-existent exception type was being caught

### Solution

**Backend (1 file):**

- `apps/api/app/nl_router.py`:
  - Changed `async with anyio.fail_after(...)` to `with anyio.fail_after(...)` (sync context manager)
  - Removed `except anyio.TooSlowError` handler (non-existent exception)
  - Changed to catch `TimeoutError` instead (raised by `anyio.fail_after()` on timeout)
  - Added `abandon_on_cancel=True` to `anyio.to_thread.run_sync()` to ensure worker thread is abandoned on cancellation

### Implementation Notes

- `anyio.fail_after()` is a sync context manager, used with `with` not `async with`
- Timeout exceptions are caught as `TimeoutError` (standard exception raised by anyio)
- Worker thread abandonment ensures cancellation works properly
- All other behavior unchanged: same error_code="llm_timeout", same routing to remote_services_unavailable

**Files changed:**

- `apps/api/app/nl_router.py` - Fixed anyio context manager usage and exception handling

---

## 2026-01-12 – Added Frontend Timeout Safety Net for Ask API Calls

Added a frontend timeout to prevent the Ask UI from hanging indefinitely if the API call stalls. The timeout aborts the request after 25 seconds and shows a user-friendly message as a normal assistant bubble.

### Problem

- API calls could hang indefinitely if network connectivity is lost or backend stalls
- No frontend safety net to abort long-running requests
- User experience degrades with indefinite "Thinking..." spinner

### Solution

**Frontend (2 files):**

- `apps/web/src/api/client.ts`:
  - Added optional `signal?: AbortSignal` parameter to `askQuestion()` method
  - Passed signal through to `fetchJson` options (fetch supports signal natively)

- `apps/web/src/pages/Ask.tsx`:
  - Added constant `FRONTEND_ASK_TIMEOUT_MS = 25000` (25 seconds)
  - Created `AbortController` and timeout timer in `handleAsk()`
  - Passed `controller.signal` to `api.askQuestion()` call
  - Added `clearTimeout(timer)` in `finally` block to prevent leaks
  - Added abort handling in `catch` block:
    - Detects `AbortError` (timeout)
    - Appends single assistant bubble with "Remote services unavailable" message (matches backend wording)
    - Uses `kind: 'normal'` styling (not error styling) for consistent UX
    - Does not set error state (no dev error panel for timeouts)
    - Resets loading state and ref guard to allow immediate retry

### Implementation Notes

- Timeout is a UX safety net; backend behavior unchanged
- Abort signal is passed through API client wrapper (minimal change)
- Timeout message matches backend error category wording exactly
- Single-flight guard (`isSendingRef`) is preserved and reset on abort
- Only one assistant bubble appended on timeout (no duplicates)
- Normal error handling path unchanged (non-abort errors still show dev panel)

### Verification

To verify the frontend timeout:

```bash
# 1. Start frontend dev server
cd apps/web
npm run dev

# 2. Test with WiFi OFF
# - Ask a question
# - Expected: Request aborts after ~25 seconds
# - Expected: "Remote services unavailable" assistant bubble appears (normal styling)
# - Expected: Loading spinner stops
# - Expected: User can immediately retry (ref guard reset)

# 3. Test with backend running normally
# - Ask a question
# - Expected: Normal behavior unchanged (no timeout if response < 25s)

# 4. Test rapid double-click / Enter
# - Expected: Single-flight guard prevents duplicate user bubbles
# - Expected: Timeout still works if triggered
```

**Files changed:**

- `apps/web/src/api/client.ts` - Added signal parameter to askQuestion
- `apps/web/src/pages/Ask.tsx` - Added timeout, abort controller, and abort handling

---

## 2026-01-12 – Fixed Double Bubble Issue in Ask Chat Transcript

Fixed intermittent "double bubble" issue where a single user action sometimes resulted in the same user message being appended twice to the chat transcript.

### Problem

- Rare duplicate user message bubbles in chat transcript
- Possible causes: double-submit (onSubmit + onClick), StrictMode/dev double-invocation, or rapid clicks
- User message was appended before async guard could prevent concurrent execution

### Solution

**Frontend (1 file):**

- `apps/web/src/pages/Ask.tsx`:
  - Added `useRef` import
  - Added `isSendingRef` ref-based single-flight guard to prevent concurrent execution
  - Guard check at start of `handleAsk`: returns early if already sending
  - Ref set to `true` at start of execution, reset to `false` in `finally` block
  - Enter key handler checks ref before calling `handleAsk` (optimization)
  - Button disabled state uses existing `loading` state (ref guard handles actual prevention)

### Implementation Notes

- Ref-based guard prevents same-tick/double-invocation issues
- User message is appended exactly once per send attempt (inside guarded function)
- No form/onSubmit duplication (no form element exists)
- Sample question clicks only set draft text (no auto-send, no duplication)
- Existing `loading` state retained for UI disabled state
- No changes to API contracts, error handling, or routing semantics

### Verification

To verify the fix:

```bash
# 1. Start frontend dev server
cd apps/web
npm run dev

# 2. Test single click on sample question
# Expected: Only one user bubble added

# 3. Test Enter key submission (Cmd/Ctrl+Enter)
# Expected: Only one user bubble added

# 4. Test Ask button click
# Expected: Only one user bubble added

# 5. Test rapid double-click on Ask button
# Expected: Only one send executes (second ignored by ref guard)

# 6. Verify normal responses and error responses still work
# Expected: No regressions in response rendering
```

**Files changed:**

- `apps/web/src/pages/Ask.tsx` - Added ref-based single-flight guard

---

## 2026-01-12 – Updated Ask Error Message Styling in Chat Transcript

Changed error message styling in Ask chat transcript to render as normal assistant bubbles instead of red error boxes.

### Changes

**Frontend (1 file):**

- `apps/web/src/pages/Ask.tsx` - Removed error-specific styling from chat transcript message rendering:
  - Error messages now use same styling as normal assistant messages:
    - `backgroundColor: 'var(--dashboard-surface)'` (was red background)
    - `border: '1px solid var(--dashboard-border)'` (was red border)
    - `color: 'var(--dashboard-text-primary)'` (was red text)
  - Clarification messages retain yellow styling (unchanged)
  - DEV-only debug panel (`AskErrorPanel`) retains red error styling (unchanged)

### Implementation Notes

- Error messages in chat transcript now appear as standard assistant bubbles
- No changes to error semantics, message text, or envelope parsing
- Bubble layout and message history behavior unchanged
- Debug panel on right side continues to use error styling for diagnostics

### Verification

To verify the change:

```bash
# 1. Start frontend dev server
cd apps/web
npm run dev

# 2. Trigger an error (e.g., invalid question or network error)
# Expected: Error message appears in chat as normal assistant bubble (not red)
# Expected: DEV debug panel on right still shows red error styling
```

**Files changed:**

- `apps/web/src/pages/Ask.tsx` - Removed error-specific styling from chat transcript

---

## 2026-01-12 – Fixed NL Clarification Behavior for Missing Parameters and Ambiguity

Fixed natural language router to properly trigger clarification responses instead of returning hard 400 "unsupported_question" errors when parameters are missing or questions are ambiguous.

### Problem

When users asked questions like "What is the latest camera original?" (without specifying shot_code), the LLM correctly identified missing parameters and generated a clarifying question, but the router returned `routing_status=unanswerable` because the LLM also returned `intent_id=null`. This violated the expected clarification loop behavior.

### Solution

**Prompt refinement:**

- Updated LLM prompt to instruct that when exactly ONE intent matches but parameters are missing, it should return that intent_id along with missing_params and user_message (not intent_id=null)
- Clarified that intent_id=null should only be used for true ambiguity between multiple intents
- Added explicit confidence guidelines for missing-param scenarios (0.60-0.79 typical)

**Routing logic changes:**

- Restructured `_apply_confidence_gates()` method to check for clarification signals (missing_params, ambiguity, user_message) BEFORE applying confidence thresholds
- First attempt with any clarification signal → NEEDS_CLARIFICATION (regardless of confidence level)
- Second attempt (is_clarification=True) with clarification signals → UNANSWERABLE (prevents loops per Appendix G)
- Only executable paths require high confidence (≥0.80) with all required params present

**Validation guardrails:**

- Added guard to prevent clarification loops (max 1 cycle per Appendix G)
- Validates intent_id exists in registry before attempting execution
- Maintains all ASK_NL_TRACE logging with updated reason strings

### Changes

**Backend (1 file):**

- `apps/api/app/nl_router.py`:
  - Updated `_build_routing_prompt()` with clearer instructions for missing-param vs ambiguity cases
  - Rewrote `_apply_confidence_gates()` to prioritize clarification detection over confidence thresholds
  - Added clarification loop prevention guard for is_clarification=True cases
  - Updated trace logging reasons to reflect new decision paths

### Behavior

**Before:**

- "What is the latest camera original?" → 400 error (unsupported_question)

**After:**

- "What is the latest camera original?" → 200 with needs_clarification, user_message: "To answer this question, I need: shot_code. Can you provide this information?"
- User provides shot_code → 200 with ok status and query results

**Constraints maintained:**

- Max 1 clarification cycle (Appendix G)
- Deterministic execution only (no dynamic SQL)
- All execution through registered intent templates
