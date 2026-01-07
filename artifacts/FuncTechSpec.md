# Functional / Technical Specification

## Production Lineage Concierge (Option A) — Phase 1

**Doc ID:** FuncTechSpec
**Version:** 0.2 (Draft)
**Date:** 2025-12-18
**Owner:** Chris Hennes
**Scope:** Phase 1 (Deterministic lineage + status + evidence)

---

## 0. Project control / governance integration

This project follows the existing control pattern used in prior repos:

- `artifacts/` contains project control docs and appendices.
- **Coding standards** and review gates are defined in `CodingStandards.md`.
- **Planned work** and sprint breakdown live in `DevPlan.md`.
- **Daily/weekly progress log** lives in `DevProgress.md`.
- This spec is the contract for Cursor CodeGen: **implement what’s here, nothing extra**.

### Required updates (as part of implementation)

- Add a `DevProgress.md` entry each time CodeGen runs:
  - prompt used (or link)
  - summary of files changed
  - what’s working / what’s blocked
  - next steps
- Any deviation from this spec must be captured as a “Decision” entry (see §11).

---

## 1. One‑sentence pitch

A small web app that ingests a tiny **OMC-shaped** dataset for a fictional production, builds a **deterministic lineage graph** from **CAPTURE → OFFLOAD/HDE → DAILIES → EDIT_EXPORT → TURNOVER → ARCHIVE**, and answers studio questions with **verifiable evidence** (events/versions/packages).

---

## 2. Goals and non‑goals

### 2.1 Goals (Phase 1)

1. **Deterministic lineage**: every asset version can be traced via `derivedFrom` edges.
2. **Deterministic status**: shot “stage” is derived from the event log.
3. **Evidence-first answers**: every answer includes supporting rows (versions/events/packages).
4. **Deployable demo**: React UI (Cloudflare Pages) + FastAPI API (Railway) + Postgres (Railway).
5. **OMC spine**: implement a minimal subset of OMC concepts sufficient to demonstrate interoperability:
   - identity, relink keys, provenance, package membership.

### 2.2 Non‑goals (Phase 1)

- No real transcoding/deBayering/media processing.
- No real DAM/MAM replacement.
- No full MovieLabs ontology implementation (we use a minimal “profile”).
- No vendor integration; seed data is mock and lives in SQL / JSON bundles.
- No LLM required for Phase 1 (NL “Ask” routes to known templates).

---

## 3. Definitions (plain English)

- **Verifiable evidence**: the specific DB records (events, versions, packages, lineage edges) that support an answer. In Phase 1, “evidence” means **our immutable-ish event log + linked metadata rows** (not external systems).

- **Production**: the project (a movie/episode) we’re tracking.
- **Shot**: a human-friendly unit of work in editorial (e.g., `010_020`).
- **Asset**: a logical thing per shot (e.g., “picture for shot 010_020”).
- **Version**: a specific representation of an asset (camera original, proxy, ProRes export, etc.).
- **Lineage / Provenance**: how a version was derived from prior versions (`derivedFrom`).
- **Package**: a delivery bundle (turnover to VFX vendor, archive package, etc.).
- **Event**: immutable audit log entry describing what happened, when, and by whom.
- **Storage URI**: pointer to where media would live; we never store media in DB.

---

## 4. User personas and workflows

### 4.1 Personas

- **Production ops / pipeline**: wants to know what’s done, what’s blocked, and why.
- **Editor / post supervisor**: needs relink keys and “latest” versions per shot.
- **Vendor coordinator**: needs package lists and delivery evidence.
- **Security / audit** (future): who accessed what, what service transformed what (Phase 2).

### 4.2 Primary workflow (Phase 1)

1. Seed/import a tiny dataset (3–5 shots).
2. Browse Dashboard: see stage counts and blocked shots.
3. Open Shot Detail: view versions, events timeline, and lineage graph.
4. Open Packages: view turnover/archive packages and members.
5. Use Ask: choose/enter a supported question → get answer + evidence.

---

## 5. System architecture

### 5.1 Frontend (React + TypeScript)

- Hosted on **Cloudflare Pages**.
- Communicates with the API via REST over HTTPS.
- Pages:
  - Dashboard
  - Shot Detail
  - Packages
  - Ask

### 5.2 Backend (FastAPI)

- Hosted on **Railway**.
- Responsibilities:
  - persistence + deterministic queries
  - data import endpoint(s)
  - “Ask” template routing (no LLM required in Phase 1)

### 5.3 Persistence (Postgres)

- Hosted on **Railway Postgres**.
- System of record:
  - `productions`, `shots`, `assets`, `versions`, `version_lineage`, `packages`, `package_members`, `events`

### 5.5 Naming vs catalog identity (DAM realism)

Real DAM/MAM systems typically treat the **internal ID + metadata** as authoritative. Filenames/folders can be:

- human-convenient (optional), or
- opaque/normalized (common), where discovery happens via search and metadata.

**Phase 1 approach:** keep original downloaded filenames as `clip_name`, but assume the “DAM path” can be opaque. We can generate stable, DAM-like URIs such as:

- `/DAM/EXFTR/assets/{asset_uuid}/versions/{version_uuid}.mp4`
- `s3://dam-demo/EXFTR/{asset_uuid}/{version_uuid}.mp4`

### 5.6 Optional manual transcoding (demo polish)

You may create a small number of “derived” files (e.g., lower bitrate proxies) using HandBrake to increase demo credibility.

- The app does **not** perform transcoding in Phase 1.
- If you create derived files, we will set `storage_uri` to point at them and set `codec/container/bitrate` fields accordingly.

### 5.4 Optional (Phase 1.5 / Phase 2): Chroma

- Not required.
- If included: store **summary docs + pointers** only (never authoritative).

---

## 6. Data model (Phase 1)

> Implementation should follow the SQL schema in `db/schema.sql` (authoritative).
> This spec describes intent and constraints.

### 6.1 Tables (summary)

- `productions`
- `shots`
- `assets`
- `versions`
- `version_lineage`
- `packages`
- `package_members`
- `events`

### 6.2 Integrity and invariants

- Every Shot belongs to exactly one Production.
- Every Asset belongs to exactly one Shot and one Production.
- Every Version belongs to exactly one Asset.
- Lineage edges are explicit and can represent multi-input transforms (Phase 2) but Phase 1 uses 1→1 chains.
- Events are append-only (no updates/deletes via API in Phase 1).

### 6.3 Minimal OMC “spine” fields

We model only these concepts:

- **Identity**: UUID PKs + external IDs (`clip_name`, `reel_or_roll`, `camera_serial`).
- **Relink keys**: fps + timecode_in/out.
- **Provenance**: `version_lineage` edges.
- **Deliveries**: packages + membership.
- **Auditability**: events with actor and tool details.

---

## 6.4 JSON storage strategy (Phase 1)

Although Phase 1 uses relational tables for core entities, we will include a few JSON columns for extensibility:

- `versions.omc_json` (JSONB): minimal OMC-shaped representation for this version (the “profile” subset).
- `versions.creative_context` (JSONB, optional): simple tags like `has_people`, `people_count_estimate`, `shot_type` (manual or future AI-suggested).
- `events.details` (JSONB): tool/run parameters, approval notes, etc.

**Indexing:** Postgres can index JSONB using GIN indexes for fast querying of common keys (we will create indexes only for keys used by templates).

## 7. Event taxonomy and stage computation

### 7.1 Required event types (Phase 1)

- `CAPTURE`
- `HDE_TRANSCODE` (or `OFFLOAD`)
- `DAILIES_PUBLISHED`
- `EDIT_EXPORT_CREATED`
- `TURNOVER_DELIVERED`
- `ARCHIVED`

### 7.2 Stage rules (Phase 1)

Stage is derived from most advanced completed event:

- `ARCHIVE` if `ARCHIVED` exists
- `TURNOVER` if `TURNOVER_DELIVERED` exists
- `EDIT_EXPORT` if `EDIT_EXPORT_CREATED` exists
- `DAILIES` if `DAILIES_PUBLISHED` exists
- `OFFLOAD` if `HDE_TRANSCODE` (or OFFLOAD) exists
- `CAPTURE` if `CAPTURE` exists
- else `NEW`

**Implementation:** `v_shot_stage` SQL view (authoritative).

---

## 8. Deterministic “Ask” question templates (Phase 1)

### 8.1 Principle

The Ask box must not “guess.” It must map to one of these **named templates** and run a deterministic query.

### 8.2 Required templates (must be implemented)

Each template returns:

- `answer` (string or structured)
- `evidence` (rows used)
- `explanation` (template name + parameters)

Templates:

1. `latest_camera_original(shot_code)`
2. `lineage_chain_to_latest_edit_export(shot_code)`
3. `shots_with_dailies_no_edit_export()`
4. `shots_ready_for_turnover_and_missing()`
5. `dailies_transform_details(shot_code)`
6. `package_members(package_id)`
7. `source_relink_keys(shot_code)`
8. `deliveries_to_vendor_last_n_days(vendor, days)`
9. `latest_versions_by_type(shot_code)`
10. `relink_conflicts()`
11. `archive_status(production_code)`
12. `highest_quality_source_for_reconform(shot_code)`

### 8.3 Ask UI behavior (Phase 1)

- Show a list of supported questions (click-to-fill).
- If user types free text:
  - Phase 1: use simple rules (keyword matching) to map to a template.
  - If mapping fails: show “Unsupported question” and list supported options.

---

## 9. UI requirements (Phase 1)

### 9.1 Dashboard

Must show:

- counts of shots by stage (NEW/CAPTURE/OFFLOAD/DAILIES/EDIT_EXPORT/TURNOVER/ARCHIVE)
- a “Blocked Shots” list with reason, e.g.:
  - “Has dailies but missing edit export”
  - “Has edit export but not delivered to vendor” (optional)

### 9.2 Shot Detail

Must show:

- shot header (scene, shot_code, description)
- versions table grouped by `version_type`
- events timeline (ordered)
- lineage visualization:
  - acceptable v0: simple vertical list with arrows (no graph lib required)
  - preferred: lightweight DAG visualization (optional)

### 9.3 Packages

Must show:

- list of packages (type, label, created_at)
- package detail shows members and the member versions

### 9.4 Ask

Must show:

- supported template list
- input (or selection)
- output:
  - answer summary
  - evidence tables (versions/events/packages)
  - explanation (template + params)

---

## 9.5 App behavior beyond queries (Phase 1)

Phase 1 supports two usage modes:

1. **Read-only demo (default):** load seed → browse → ask. No workflow operations.
2. **Lightweight “advance state” operations (optional but recommended):**
   - The UI can provide buttons such as “Publish Dailies”, “Create Edit Export”, “Deliver Turnover”, “Archive”.
   - Each button calls a deterministic API that creates:
     - one new `version` (if applicable),
     - one `version_lineage` edge,
     - one `event` row.
   - This demonstrates the **state machine** nature of pipelines without implementing real media processing.

If we implement mode (2), the seed dataset still loads the initial camera originals; the user actions create later stages.

## 10. API requirements (Phase 1)

- FastAPI must implement the endpoints in **Appendix A (API Definition)**.
- All endpoints return JSON.
- Error responses are structured:
  - `{"error": {"code": "...", "message": "...", "details": {...} } }`

---

## 11. Decisions log (required discipline)

Create a `Decisions` section in `DevProgress.md` with entries formatted:

- **Decision:** <short>
- **Date:** 2025-12-18
- **Rationale:** <why>
- **Impact:** <what changes>

---

### 12.1 Seed/data population ownership

Yes: we will create an explicit, deterministic data population mechanism:

- `db/seed.sql` for baseline data (camera originals + core metadata)
- `POST /import/seed` to apply seed and (optionally) reset
- `apps/api/app/seed/` helpers to keep the dataset maintainable

The dataset is the heart of the POC; we will treat it as a first-class artifact and keep it under version control.

## 12. Acceptance criteria (Phase 1 “Definition of Done”)

The project is done when:

1. App deploys:
   - web on Cloudflare Pages
   - API + Postgres on Railway
2. Seed dataset loads successfully and produces 3–5 shots with complete chains (with at least one blocked case).
3. Dashboard shows correct stage counts and blocked list.
4. Shot Detail shows:
   - versions
   - events
   - lineage chain
5. Packages page shows turnover/archive packages and members.
6. Ask page answers all 12 templates with:
   - deterministic answer
   - evidence tables
   - explanation block

---

## Appendix A — API Definition (authoritative contract)

### A.1 Import / seed

#### `POST /import/seed`

Loads the demo dataset (idempotent preferred).

**Request:** none, or optional `{"mode":"reset_and_seed"}`
**Response:**

```json
{ "ok": true, "production_code": "EXFTR", "shots_loaded": 5 }
```

### A.2 Productions

#### `GET /productions`

**Response:**

```json
{ "productions": [{ "code": "EXFTR", "title": "Example Feature (Demo)" }] }
```

### A.3 Shots

#### `GET /shots?production_code=EXFTR`

**Response (summary):**

```json
{ "shots": [{ "shot_code": "011_021", "scene": "011", "stage": "DAILIES" }] }
```

#### `GET /shots/{shot_code}?production_code=EXFTR`

**Response (detail):**

```json
{
  "shot": { "shot_code": "011_021", "scene": "011", "description": "..." }
}
```

#### `GET /shots/{shot_code}/lineage?production_code=EXFTR`

**Response:**

```json
{
  "shot_code": "011_021",
  "chain": [{ "version_type": "EDIT_EXPORT", "version_id": "...", "derived_from": "..." }]
}
```

### A.4 Packages

#### `GET /packages?production_code=EXFTR`

#### `GET /packages/{package_id}`

#### `GET /packages/{package_id}/members`

### A.5 Events

#### `GET /shots/{shot_code}/events?production_code=EXFTR`

### A.6 Ask (deterministic templates)

#### `POST /ask`

**Request:**

```json
{
  "production_code": "EXFTR",
  "question": "For shot 011_021, show lineage camera→edit export"
}
```

**Response:**

```json
{
  "template":"lineage_chain_to_latest_edit_export",
  "params": {"shot_code":"011_021"},
  "answer": "...",
  "evidence": {
    "versions":[...],
    "events":[...],
    "packages":[...]
  }
}
```

---

### A.7 Optional workflow ops (state machine demo)

These endpoints are optional. If implemented, they must be deterministic and only create metadata + events.

#### `POST /shots/{shot_code}/ops/publish_dailies`

Creates `DAILIES_PROXY` version (if missing) derived from latest `HDE_MASTER`, and emits `DAILIES_PUBLISHED` event.

#### `POST /shots/{shot_code}/ops/create_edit_export`

Creates `EDIT_EXPORT` version derived from latest `DAILIES_PROXY`, and emits `EDIT_EXPORT_CREATED` event.

#### `POST /shots/{shot_code}/ops/deliver_turnover`

Adds latest `EDIT_EXPORT` to a TURNOVER package and emits `TURNOVER_DELIVERED` event.

#### `POST /shots/{shot_code}/ops/archive`

Adds latest “highest quality source for reconform” to an ARCHIVE package and emits `ARCHIVED` event.

## Appendix B — Environment variables

API:

- `DATABASE_URL` (Railway Postgres)
- `CORS_ORIGINS` (Cloudflare Pages URL)
- `APP_ENV` (local/dev/prod)

Web:

- `VITE_API_BASE_URL`

---

## Appendix C — Seed dataset requirements (Phase 1)

- 3–5 shots.
- Each shot has:
  - CAMERA_ORIGINAL → HDE_MASTER → DAILIES_PROXY
- At least 1 shot lacks EDIT_EXPORT to demonstrate “blocked”.
- At least 1 turnover package (3 shots).
- At least 1 archive package (2 shots).
- At least 1 relink conflict scenario (same clip_name different camera_serial or fps) for template #10.

---

## Appendix D — Testing requirements (Phase 1)

- API unit tests for each Ask template query (golden outputs).
- Basic integration test: seed → list shots → shot detail → packages → ask.

## Appendix E — Ask Error Handling & Observability (Demo-Safe Requirement)

This appendix defines **mandatory error-handling and logging behavior** for the Ask feature.
Its purpose is to ensure the system is **demo-safe, trustworthy to non-technical users, and diagnosable by operators**, without leaking internal implementation details.

This appendix is **normative** for Phase 1 and later phases.

---

### E.1 Design principles

1. **Users must never see raw technical errors**
   - No HTTP status codes
   - No stack traces
   - No SQL, library, or framework names

2. **Errors must be explainable at a human level**
   - The user should understand _what kind_ of problem occurred
   - The user should not be exposed to _why_ it occurred internally

3. **All failures must be observable**
   - Every Ask failure must be logged with sufficient detail to diagnose issues after the fact
   - Logging must be reliable in both local development and deployed environments

---

### E.2 User-facing error states (Ask UI)

The Ask UI MUST present exactly **two** user-visible error messages.

#### E.2.1 Unanswerable question

Displayed when the system cannot deterministically map the user’s input to a supported Ask template, including:

- unsupported questions
- ambiguous questions
- routing / intent resolution failures
- non-deterministic or unsafe interpretations

**User message (exact text):**

> **This question can’t be answered**
> The system couldn’t map your question to a supported, verifiable query.
> Please select one of the supported questions or rephrase your request.

Typical HTTP status:

- `400` or `422`

Typical internal error codes:

- `unsupported_question`
- `ambiguous_question`

---

#### E.2.2 Data retrieval failure

Displayed when the system _could plausibly answer the question_ but encounters an internal failure, including:

- SQL or query errors
- template implementation bugs
- database connectivity failures
- unexpected backend exceptions

**User message (exact text):**

> **Unable to retrieve data**
> The system encountered an internal error while answering this question.
> Please contact your system administrator for assistance.

Typical HTTP status:

- `500`

Typical internal error codes:

- `template_error`
- `query_execution_error`
- `internal_error`

---

### E.3 Developer-visible diagnostics (development only)

In **development environments only**, the Ask UI MUST provide a collapsible “Show Error Details” section containing diagnostic metadata, including:

- HTTP status code
- request URL
- backend error code
- backend error message
- timestamp

These diagnostics MUST NOT be shown in production or demo environments.

Environment gating should be performed using standard build/runtime flags (e.g. `DEV`, `APP_ENV`, or equivalent).

---

### E.4 API error envelope contract

The `/api/ask` endpoint MUST return a structured JSON error envelope on all failures.

Minimum required shape:

```
{
  "detail": {
    "code": "<string>",
    "message": "<string>",
    "category": "<string optional>"
  }
}
```

Notes:

- `code` MUST be stable and machine-readable
- `message` MAY contain internal diagnostic text
- `category` MAY be used to group errors but is not user-visible
- The UI MUST NOT display `message` directly to users in production

---

### E.5 Logging & observability requirements

All Ask failures MUST be logged as **structured JSON** to stdout on the API server.

This is sufficient for:

- local development (terminal output)
- deployed environments (Railway captures stdout)

Minimum required logged fields:

- timestamp (ISO-8601)
- environment (local / dev / prod)
- endpoint (`/api/ask`)
- production_code
- user question
- resolved template name (if any)
- error code
- error category
- exception message
- stack trace (when available)

Example (illustrative):

```
{
  "timestamp": "2026-01-05T21:14:32Z",
  "environment": "local",
  "endpoint": "/api/ask",
  "production_code": "EXFTR",
  "question": "Show lineage chain to latest edit export for shot 011_021",
  "template": "lineage_chain_to_latest_edit_export",
  "error_code": "template_error",
  "error_category": "data_retrieval_failure",
  "exception": "(psycopg2.errors.SyntaxError) syntax error at or near \"UNION\"",
  "stack_trace": "..."
}
```

Sensitive information (credentials, secrets, tokens) MUST NOT be logged.

---

### E.6 Non-goals (explicit)

- No error persistence database is required for Phase 1
- No external logging or monitoring service is required
- No user-configurable error behavior
- No automatic retries in the Ask path

---

### E.7 Acceptance criteria

The Ask feature satisfies this appendix when:

1. The UI never displays raw HTTP status codes or backend exception text
2. All Ask failures render one of the two defined user messages
3. Developer diagnostics are visible only in development
4. Backend logs contain sufficient structured data to diagnose failures
5. The system remains fully deterministic and demo-safe

---

End of Appendix E.

## Appendix F — SQL Query Contracts, Constraints, and Response Shape

This appendix captures implementation constraints and clarifications discovered during development of SQL-backed query behavior across the system. All items herein are considered normative and apply to all current and future queries, regardless of feature or UI surface.

### F.1 Deterministic Query Behavior

All SQL-backed queries in Phase 1 are deterministic and non-generative.

Each query maps to:

- A fixed intent or template identifier
- A bounded SQL query (or bounded query set)
- A fixed response schema

The system does not infer, embellish, or extrapolate beyond query results. Sparse or summary-only responses are intentional and correct when aligned with the defined query intent.

### F.2 PostgreSQL SQL Constraints

To ensure correctness and compatibility with PostgreSQL, the following constraints MUST be observed:

- `COUNT(DISTINCT ...) FILTER (WHERE ...)` MUST NOT be used.
  PostgreSQL does not support `FILTER` with `COUNT(DISTINCT ...)`.

- Conditional distinct counts MUST use the following pattern:
  `COUNT(DISTINCT CASE WHEN <condition> THEN <id> END)`

- All `UNION` / `UNION ALL` statements MUST:
  - Return the same number of columns
  - Use identical column ordering
  - Use explicit column aliases in every SELECT
  - Return compatible data types at each column position

Failure to meet these constraints will result in runtime SQL errors and is considered an implementation defect.

### F.3 Evidence and Response Shape Contracts

API response schemas enforce strict typing.

- Any response field defined as a list MUST always be returned as a list, even when a query yields a single row.
- Returning an object where a list is expected will trigger a response validation error and result in a server-side failure.

This constraint is intentional and ensures UI stability, audit consistency, and forward compatibility as queries evolve.

### F.4 Aggregate vs. Detail Semantics

Some queries are explicitly defined to return aggregate or summary-level information only.

- Aggregate queries MAY return counts, totals, or health indicators without per-entity detail.
- The absence of row-level detail in such queries is intentional and MUST NOT be treated as incomplete data.

Drill-down or per-entity detail queries must be implemented as separate, explicitly defined query intents.

### F.5 Error Handling Guarantees

For all SQL-backed queries:

- SQL syntax errors MUST surface as explicit API errors
- Schema mismatches MUST fail during response serialization
- Silent coercion, implicit reshaping, or automatic structural correction of data is forbidden

These guarantees prioritize correctness, auditability, and long-term system integrity.
