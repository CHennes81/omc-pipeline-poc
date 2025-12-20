# DevPlan.md

## Project
MovieLabs OMC – Production Lineage Concierge (POC)

## Purpose
This DevPlan defines **what will be built and in what order** for the Production Lineage Concierge proof-of-concept.

This project is a **thinking artifact** intended to demonstrate:
- Deep understanding of MovieLabs Ontology (OMC v2.8)
- Deterministic asset identity, versioning, and lineage
- Clean architectural reasoning (metadata-first, system-of-record)
- Ability to rapidly design and generate a real web app using Cursor

This is **not** production software.

---

## In Scope
- Deterministic pipeline modeling
- Metadata-only transformations
- Inspectable lineage and audit history
- Evidence-based “Ask” responses
- React + FastAPI + PostgreSQL implementation

## Out of Scope
- Real media processing
- AI / LLM inference
- Vector databases
- DAM replacement
- UI polish beyond clarity

---

## Phase 1 – Core Deterministic Pipeline (Primary POC)

### 1. Data Model & Database
- PostgreSQL relational core
- Tables:
  - productions
  - shots
  - assets
  - versions
  - events
  - packages
- JSONB columns for OMC-shaped payloads
- Deterministic UUIDs only
- Explicit lineage via `derived_from_version_id`
- Canonical view:
  - `v_shot_stage` (current lifecycle stage per shot)

### 2. Seed Dataset
- 12 camera-original stand-ins (Pexels MP4s)
- Filenames preserved as `clip_name`
- Media referenced via opaque DAM-style URIs
- Seed includes:
  - Production
  - Shots
  - Initial assets
  - Initial versions and events

### 3. Backend (FastAPI)
- REST API per FuncTechSpec Appendix A
- Deterministic behavior only
- Explicit error models
- No AI calls
- No background processing

### 4. Frontend (React + TypeScript)
- Pages:
  - Dashboard (productions / shots)
  - Shot detail (versions, lineage, events)
  - Packages / deliveries
  - Ask (deterministic queries)
- Evidence-first UI:
  - Tables
  - IDs
  - Timestamps
  - No prose without backing data

### 5. Ask Templates
- Fixed question templates only
- Each answer returns:
  - Direct answer
  - Evidence rows
  - Source table references
- No free-text generation

---

## Phase 2 – Optional (If Time Allows)
- Simple lineage graph visualization
- Read-only audit export
- Hosted deployment (Railway + Cloudflare Pages)

---

## Completion Criteria
- App runs locally
- Lineage is deterministic and inspectable
- Audit trail is complete
- Ask questions are evidence-backed
- Ready for guided studio walkthrough
