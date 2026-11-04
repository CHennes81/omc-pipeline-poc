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
- `DEBAYER_TRANSCODE` (or `OFFLOAD`)
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
- `OFFLOAD` if `DEBAYER_TRANSCODE` (or OFFLOAD) exists
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
{ "shots": [{ "shot_code": "011_002", "scene": "011", "stage": "DAILIES" }] }
```

#### `GET /shots/{shot_code}?production_code=EXFTR`

**Response (detail):**

```json
{
  "shot": { "shot_code": "011_002", "scene": "011", "description": "..." }
}
```

#### `GET /shots/{shot_code}/lineage?production_code=EXFTR`

**Response:**

```json
{
  "shot_code": "011_002",
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
  "question": "For shot 011_002, show lineage camera→edit export"
}
```

**Response:**

```json
{
  "template":"lineage_chain_to_latest_edit_export",
  "params": {"shot_code":"011_002"},
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

Creates `DAILIES_PROXY` version (if missing) derived from latest `CAMERA_MASTER`, and emits `DAILIES_PUBLISHED` event.

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
  - CAMERA_ORIGINAL → CAMERA_MASTER → DAILIES_PROXY
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

The Ask UI MUST present exactly **three** user-visible error messages.

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

#### E.2.3 Remote services unavailable

Displayed when the system cannot reach a required remote dependency (such as an LLM API), or when a request to that dependency times out.

**User message (exact text):**

> **Remote services unavailable**
> The system couldn’t reach a required remote service to answer this question.
> Please try again later or contact your system administrator.

Typical HTTP status:

- `503` (Service Unavailable) when a remote dependency is unavailable or times out
- `500` (Internal Server Error) when the failure is surfaced indirectly via internal handling logic

Typical internal error codes:

- `remote_services_unavailable`
- `llm_timeout`
- `llm_connection_error`

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
  "question": "Show lineage chain to latest edit export for shot 011_002",
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
2. All Ask failures render one of the three defined user messages
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

---

End of Appendix F.

## Appendix G — Natural Language Query Processing (Deterministic Routing)

### Purpose

This appendix defines the **Natural Language (NL) Ask** capability: a user may enter a free‑form question, and the system will attempt to **map it deterministically** to a **supported intent** and execute a **predefined deterministic query path** (initially SQL templates; later Stored Procedures), or **reject** the request safely.

This appendix is explicitly designed to preserve the system’s core principles:

- **Deterministic execution**: no dynamic SQL generation; no hallucinated joins/fields.
- **Auditable routing**: every NL request resolves to a known intent (or rejection), with a recorded trace of the decision.
- **Demo‑safe UX**: uncertainty yields clarification or rejection—not confident wrong answers.
- **Separation of concerns**: NL routing is a translation layer; **data truth** comes only from deterministic query execution.

---

### Non‑Negotiable Guarantees (Natural Language Contract)

The NL Ask interface MUST enforce the following user‑visible guarantees:

1. **Bounded capability**
   - The system can only answer questions that map to an intent in the **Intent Registry**.
   - If a request cannot be mapped, it is rejected as **unsupported**.

2. **No invented parameters**
   - The NL layer MUST NOT guess missing required parameters.
   - If required parameters are missing, the system asks a single clarifying question (see “Clarification Loop”), or rejects if a second pass still cannot proceed.

3. **No invented data**
   - The NL layer MUST NOT fabricate results.
   - All answers MUST be derived from deterministic query execution.

4. **Deterministic failure**
   - The system MUST choose one of the explicit outcomes:
     - `ok`
     - `needs_clarification`
     - `unanswerable`
     - `error`
   - It MUST NOT “retry until it works” or loop through alternate prompts/tooling.

5. **Explainable routing**
   - Responses MUST include the chosen `intent_id` (when applicable) and the validated parameters used for execution.
   - When rejected, the response MUST indicate whether the reason was **unsupported**, **ambiguous**, **missing parameters**, or **invalid parameters**.

---

### Definitions

**Intent**
A named, bounded, deterministic query capability (e.g., “archive status for a production”) with:

- A stable `intent_id`
- A strict parameter contract (required/optional, types, constraints)
- A deterministic execution binding (SQL template today; Stored Procedure later)
- A fixed response schema

**Intent Registry**
The authoritative list of supported intents and their contracts. It is the “menu” of what NL Ask can do.

**Intent Retrieval**
The process of providing intent definitions to the NL router. In v0 this is a static load of the registry. A future RAG‑powered implementation MAY replace this without changing routing semantics.

---

### Feature Flags & Modes (ENVVAR‑Controlled)

NL Ask behavior MUST be controlled via environment variables to support safe rollout and demo posture.

#### Required ENVVARs

**Default & Failure Behavior**

- The OpenAI API key MUST be supplied via an environment variable (e.g., `OPENAI_API_KEY`) and MUST NOT be embedded in source code or committed configuration files.

- If any NL-related ENVVAR is missing, unreadable, or invalid, the system MUST default to **production-safe behavior**:
  - NL routing disabled
  - Deterministic Ask mode only
  - Dual-mode UI hidden
  - No LLM calls permitted

- `ASK_NL_ENABLED` (boolean; default `false`)
  - If `false`, the backend MUST NOT call the LLM router and MUST reject NL mode requests.
- `ASK_DUAL_MODE_UI` (boolean; default `false`)
  - If `true` and NL is enabled, the UI MAY expose a “Switch mode” link.
- `ASK_DEFAULT_MODE` (`deterministic` | `nl`; default `nl`, effective only when NL is enabled and a provider key is configured)
  - Determines which mode the Ask page starts in.

#### Confidence Threshold ENVVARs (initial defaults; tunable)

- `ASK_NL_CONFIDENCE_MIN` (float; default `0.80`)
  - Minimum confidence required to accept a routing decision as executable.
- `ASK_NL_CONFIDENCE_CLARIFY_MIN` (float; default `0.60`)
  - Minimum confidence required to offer a clarification question. Below this threshold, reject as `unanswerable`.

---

### UX Requirements (Ask Page)

#### Sample Questions (Dropdown)

- The existing “supported questions” list SHOULD be presented as **Sample Questions** in a dropdown.
- Selecting a sample question SHOULD prepopulate the NL text box with a usable example (including obvious placeholders for required parameters).
- Users MAY edit the prepopulated text and submit.

#### Mode Switching

- When `ASK_DUAL_MODE_UI=true` AND `ASK_NL_ENABLED=true`, the UI SHOULD display a small link that toggles between:
  - **Deterministic** mode (safe)
  - **Natural Language** mode (beta)
- When dual‑mode is disabled, the mode link MUST NOT render.

#### Help / Examples in NL Mode

- In NL mode, the UI SHOULD still show sample questions as examples of supported capabilities.
- The UI MAY provide a small “Help” panel listing 3–7 example prompts, ideally including **at least one representative example per intent** when feasible.

#### Clarification Display

When the backend returns `needs_clarification`, the UI MUST:

- Display the returned `user_message` as a clean, human‑readable prompt (not raw JSON)
- Allow the user to respond in the same Ask input
- Submit the user’s clarification as a second routing attempt (see “Clarification Loop”)

---

### NL Routing Architecture (Component Responsibilities)

#### 1) Application Responsibilities (Pre‑LLM)

Before calling the LLM router, the application MUST:

- Accept the user’s input text and basic session context (e.g., selected production)
- Load supported intents from the Intent Registry (or a retrieved subset)
- Construct a routing prompt that includes:
  - The Natural Language Contract rules (above)
  - The allowable `intent_id` set
  - Parameter contracts and constraints
  - Output schema requirements (JSON only; no prose)
- Enforce feature flags (`ASK_NL_ENABLED`) and mode selection

#### 2) LLM Responsibilities (Router Only)

The LLM MUST perform only:

- **Intent selection** from the allow‑list
- **Parameter extraction** from the user’s text (and optional session hints)
- **Uncertainty reporting** via:
  - `missing_params`
  - `ambiguity`
  - `confidence`
  - optional `user_message` (one question maximum)

The LLM MUST NOT:

- Generate SQL
- Claim it has executed queries
- Invent IDs/values when missing

#### 3) Application Responsibilities (Post‑LLM)

After receiving the LLM response, the application MUST:

- Validate the response as schema‑compliant JSON
  - If invalid: return `unanswerable` (no retries)
- Validate `intent_id` exists in registry
- Validate parameter keys, types, and constraints
- Apply confidence gates in the following order:
  - If `confidence >= ASK_NL_CONFIDENCE_MIN` and no ambiguity and no missing required params → executable
  - Else if this is the **initial interpretation attempt**, `confidence >= ASK_NL_CONFIDENCE_CLARIFY_MIN`, and the request is potentially resolvable (e.g., missing required parameters or ambiguous intent) → return `needs_clarification`
  - Else → `unanswerable`

- Execute the deterministic query path via `AskExecutor` (see below)
- Return response + evidence in the established Ask response shape

---

### Clarification Loop (One Follow‑Up Maximum)

The NL Ask interface supports at most **one** clarification question per user request:

1. User submits NL question
2. Router returns either:
   - executable intent + params (`ok`), or
   - `needs_clarification` with a single `user_message`
3. User provides clarification input
4. System performs exactly one additional routing pass using:
   - original question
   - clarification answer
5. If still not executable after this second pass → `unanswerable` (the system MUST NOT return `needs_clarification` on the second attempt)

This constraint MUST be enforced to avoid looping behavior and to keep UX predictable.

---

### Intent Registry (Authoritative “Supported Universe”)

The Intent Registry MUST be stored as a **single canonical JSON file** in the repo, tracked via version control, and containing an explicit internal `registry_version` (v0). Historical versions are managed by Git; filenames MUST remain stable.

#### Registry Requirements

- Registry is loaded at application startup (or cached)
- Each intent entry MUST include:
  - `intent_id` (stable identifier; immutable once published)
  - `title`
  - `description`
  - `required_params` (name, type, constraints, description)
  - `optional_params` (name, type, constraints, description)
  - `execution` binding:
    - `kind`: `sql_template` | `stored_procedure`
    - `template_id` (if `sql_template`)
    - `sp_name` + arg mapping (if `stored_procedure`)
  - `response_schema_id` (or reference to existing response model)

#### Example Intent Entry (Illustrative)

```json
{
  "intent_id": "archive_status",
  "title": "archive status for a production",
  "description": "Return whether a production has been archived and summarize relevant evidence.",
  "required_params": {
    "production_code": {
      "type": "string",
      "pattern": "^[A-Z0-9]{3,10}$",
      "description": "Production code, e.g., EXFTR"
    }
  },
  "optional_params": {},
  "execution": {
    "kind": "sql_template",
    "template_id": "archive_status"
  },
  "response_schema_id": "ask_archive_status_v1"
}
```

> Note: the registry is authoritative. It may represent a subset of templates described elsewhere in the spec.

---

### LLM Router Request / Response Contract

#### Request (Conceptual)

The router request MUST include:

- User question text
- Optional session hints (e.g., selected production)
- A set of allowed intents (full registry or retrieved subset)
- Parameter constraints
- The output schema definition and strict instructions:
  - JSON only
  - no prose
  - no additional keys

#### Response (Schema Requirements)

The LLM MUST return JSON conforming to a strict schema with these top‑level fields:

- `intent_id`: string | null
- `confidence`: float (0–1)
- `params`: object (key/value pairs)
- `missing_params`: array of strings
- `ambiguity`: null | object containing candidate intents
- `user_message`: null | string (single clarification question; REQUIRED when `status = needs_clarification` on the first attempt)

The application MUST treat any schema violation as `unanswerable`.

#### User‑Facing Messaging

- `user_message` is free‑form text intended for display.
- The UI MUST present it cleanly (no JSON formatting).
- The application MAY enforce safety constraints:
  - max length
  - one question
  - no claims of execution (“I looked up…”) prior to deterministic execution

---

### Deterministic Execution Layer (AskExecutor)

To decouple NL routing from query implementation details, execution MUST occur through a thin execution interface:

- `AskExecutor` (interface / protocol)
  - `execute(intent_id, params) -> AskResponse`

#### Implementations

- `SqlTemplateExecutor` (v0)
  - Uses existing SQL templates in code
- `StoredProcedureExecutor` (future)
  - Calls deterministic stored procedures
  - Returns the exact same response schema as`SqlTemplateExecutor` above

#### TODO / Refactor Hooks

- TODO: introduce `StoredProcedureExecutor` and migrate one high‑value intent as a proof of pattern (future)
- TODO: move all SQL out of code and into stored procedures while keeping `AskExecutor` stable (future)

---

### Intent Retrieval Hook (Future RAG Placeholder)

To support future RAG‑based intent retrieval without altering behavior:

- Introduce an `IntentRetriever` abstraction:
  - `get_candidate_intents(user_text, session_context) -> [IntentDefinition]`

#### v0 Implementation

- `StaticIntentRetriever` returns all intents (or a simple subset rule)

#### Future Implementation (Optional)

- `RagIntentRetriever` uses embeddings to retrieve the top‑K relevant intent definitions and examples
- This improves prompt size and routing accuracy but MUST NOT change determinism rules

---

### Logging & Observability (NL + Ask)

NL Ask MUST log enough data to reconstruct every decision and handoff.

Minimum requirements (structured logs preferred):

1. **API ingress**
   - `request_id`, timestamp
   - mode (`deterministic` | `nl`)
   - raw user input
   - session context identifiers (if any)

2. **Router call**
   - prompt metadata (model id, version, token counts if available)
   - router response (raw JSON)
   - schema validation result
   - confidence gates outcome

3. **Execution**
   - `intent_id`
   - validated params
   - execution binding (`template_id` or `sp_name`)
   - query timing metrics
   - row counts / evidence counts (avoid logging massive payloads unless explicitly enabled)

4. **API egress**
   - response status (`ok` | `needs_clarification` | `unanswerable` | `error`)
   - error code (if any)

---

### Deterministic Error Semantics (NL Layer)

The NL layer MUST map outcomes into the existing Ask error semantics:

- `needs_clarification`
  - missing required parameters, or ambiguous intent, or low confidence above clarify threshold
- `unanswerable`
  - unsupported intent
  - low confidence below clarify threshold
  - schema validation failure
  - second-pass clarification still not executable
- `error`
  - deterministic execution failed (DB error, etc.) with explicit error handling as defined elsewhere in the spec

---

End of Appendix G.

# Appendix H — Seed Data Specification (Final)

## H.1 Purpose and Scope

This appendix defines the authoritative specification for regenerating **demo seed data** for the OMC Ontology PoC.

The intent is to produce a **realistic, narrative-rich dataset** that reflects modern episodic production practices while **fitting entirely within the existing database schema**. No schema changes are permitted.

This seed data:

- Replaces **all existing demo data**
- Represents **a single episodic production**
- Is optimized for **executive-facing demos**, not operational completeness

---

## H.2 Production Assumptions

- **Production Type:** High-budget episodic television
- **Production Count:** 1 (single production only)
- **Shoot Days:** 3 consecutive shoot days
- **Scenes:** Multiple scenes spanning all shoot days
- **Total Shots:** 28 shots total across all days
- **Camera System:** ARRI ALEXA Mini LF family (standardized for entire production)
- **Audio:** Out of scope for this PoC (video-only lineage)

---

## H.3 Shot Identity Model

### H.3.1 Shot Naming Convention (Human-Readable)

Shots are identified in human-facing contexts using a conventional format:

```
<SceneNumber>_<ShotNumber><Variant><Modifier?>
```

Examples:

- `011_001`
- `011_001A`
- `011_001B`
- `011_003C_PU`

These strings reflect **real-world script supervisor practices** and are intentionally non-normalized.

### H.3.2 Canonical Shot Identity (System Model)

The **authoritative identity** of a shot is defined via metadata, not string parsing.

Each shot asset must include:

- `base_shot_code`: e.g. `011_001`
- `variant_code`: e.g. `A`, `B`, `C` (nullable)
- `human_readable_code`: full string label as shown above

All lettered variants (`A`, `B`, `C`, etc.) reference the same `base_shot_code`.

String parsing must never be used to infer relationships.

---

## H.4 Lettering Up (Setup Changes)

“Lettering up” is used when camera setups change for the same scripted shot.

- The first setup uses the base shot code (e.g., `011_001`)
- Subsequent setups increment the variant (`011_001A`, `011_001B`, etc.)
- Each variant represents a **distinct camera setup**
- All variants remain logically grouped via `base_shot_code`

This practice is common and must be reflected in the seed data.

---

## H.5 Pickups and Partials (Out of Scope)

Partial shots or pickups (e.g., `011_003C_PU`) are **acknowledged but intentionally excluded** from this seed dataset.

Notes:

- In real productions, pickups are often labeled inconsistently
- They may represent partial performances or dialogue-only segments
- Future work may model these using the same metadata approach as lettered variants

For this PoC:

- No pickup-specific assets are generated
- The data model is assumed to support them in the future

---

## H.6 Shot Distribution and Rework Narrative

### H.6.1 Distribution

- 28 total shots across 3 shoot days
- Majority progress smoothly through the pipeline
- A small subset require rework

### H.6.2 Rework Cases

Exactly **4 shots** must require rework, distributed as:

- 2 editorial re-cuts
- 1 VFX revision
- 1 creative rework (director or studio notes)

Each rework must include:

- Clear lineage from prior version(s)
- A human-readable reason (stored in metadata or notes)
- New downstream assets reflecting the revision

---

## H.7 Temporal Realism

Timestamps must tell a believable production story.

Guidelines:

- Camera Originals created during shoot days
- Camera Masters generated hours later
- Dailies generated same day or overnight
- Editorial outputs occur days later
- Reworked assets occur after original deliveries

No two assets should share identical timestamps unless logically required.

---

## H.8 Camera Metadata (ARRI ALEXA Mini LF)

### H.8.1 Minimum Required Metadata (PoC)

Each Camera Original and Camera Master must include at least:

- camera_make: ARRI
- camera_model: ALEXA Mini LF
- serial_number
- lens_model
- focal_length_mm
- aperture
- iso
- frame_rate
- resolution
- codec
- color_space
- timecode_start
- timecode_end
- capture_timestamp

### H.8.2 Reference Metadata (Non-Mandatory)

ARRI publishes a significantly larger metadata set.
This PoC requires only the subset above.

A full reference list may be appended later for completeness, but seed generation must populate **at least** the required subset.

---

## H.9 Lineage and DAG Constraints

- Lineage must form a **Directed Acyclic Graph**
- Downstream assets may have **multiple parents**
- Editorial outputs conceptually derive from multiple source shots
- This PoC models simplified, deterministic parentage only

The data must remain DAG-safe under all transformations.

---

## H.10 Destructive Reseed Requirement

Running the seed generator under this spec must:

- Delete or overwrite **all prior demo data**
- Create only the new dataset defined here
- Leave all application logic unchanged
- Leave all schemas unchanged

If any data element does not fit the existing schema, it must be adapted via metadata — **not structural change**.

---

## H.11 Non-Goals

This appendix explicitly does not attempt to model:

- Audio assets
- Editorial EDL/AAF ingestion
- Pickups or partials
- Multi-production tenancy
- Real-time ingest systems

These are intentionally deferred.

---

## H.12 Summary

This seed dataset is designed to:

- Be realistic enough to resonate with studio technologists
- Be simple enough to explain clearly to executives
- Demonstrate the power of deterministic lineage capture
- Align cleanly with MovieLabs 2030 OMC principles

It is a narrative dataset, not a production system.
