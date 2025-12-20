# DevProcess.md

## Purpose
This document defines **how work is performed** on the MovieLabs OMC – Production Lineage Concierge (POC).

This project uses **formal governance**, even though it is a POC.

---

## Sources of Truth
1. FuncTechSpec.md (authoritative)
2. DevPlan.md
3. DevProcess.md
4. DevProgress.md

If there is a conflict, **FuncTechSpec.md wins**.

---

## Development Principles
- Deterministic over clever
- Metadata first
- Inspectable over impressive
- Evidence before explanation
- No speculative features

---

## Cursor CodeGen Rules
Cursor is treated as an AI collaborator.

Every Cursor CodeGen run MUST:
- Explicitly reference FuncTechSpec.md
- Implement only what is specified
- Avoid adding “helpful extras”
- Append a factual summary to DevProgress.md

Cursor must NOT:
- Introduce AI / LLM calls
- Introduce vector databases
- Change ontology semantics
- Invent workflow steps

---

## Workflow
1. Prepare or confirm control docs
2. Run Cursor CodeGen for a coherent unit of work
3. Review generated output manually
4. Apply fixes if required
5. Append execution summary to DevProgress.md
6. Commit with a clear message

---

## Branching & Commits
- Single `main` branch (POC)
- Small, logical commits
- Commit messages must be descriptive
- No “WIP” commits

---

## Logging Discipline
DevProgress.md is:
- Append-only
- Chronological
- Factual
- Non-speculative

Each entry should record:
- Date
- What was generated or changed
- What remains incomplete
- Known issues or follow-ups

---

## What This Is Not
- Agile theater
- Sprint velocity tracking
- Feature brainstorming
- AI experimentation sandbox
