# Commit Message Guide

> **Version History**
>
> - 2025‑12‑10 – v1.1 – Aligned with Conventional Commits, clarified branch/tag naming, and linked commit practices to versioning and release metadata.
> - 2025‑11‑xx – v1.0 – Initial version prior to control‑doc consolidation.

---

This project uses **Conventional Commits**. Husky + commitlint will reject messages that don’t follow this format.

## Basic Format

```text
<type>(optional-scope): <short description>
```

- All lowercase for the `<type>` and scope.
- Use imperative mood for the description (e.g., “add login screen”, not “added login screen”).

## Common Types

- `feat` – New features or user-visible behavior.
- `fix` – Bug fixes.
- `style` – Visual/UI-only changes (CSS/layout) with no behavior changes.
- `refactor` – Code changes that are not bug fixes or features.
- `docs` – Documentation changes (README, specs, etc.).
- `test` – Adding or updating tests.
- `chore` – Build tools, configs, or other non-product code changes.

## Examples for This Repo

- `feat(web): add cinematic login screen`
- `feat(web): implement mocked localization workspace`
- `style(workspace): stack controls and refine language selector`
- `refactor(services): simplify mock localization pipeline`
- `docs(artifacts): update sprint 1 notes`

## Tips

- Keep descriptions short but specific.
- Group related changes into one commit instead of many tiny commits.
- If a commit touches multiple areas, choose the most representative scope or omit the scope entirely.

## Appendix "A": SOP — Squash `dev` → `main`, then reset `dev` to match `main`

This SOP documents the **canonical workflow** we use to keep a clean, linear history on `main` **and** a long‑lived, stable `dev` branch.

> **Core principle:** After a squash merge, you **do not rebase** `dev` onto `main`.
> You **hard‑reset** `dev` to `main` and force‑push with lease.

---

### When to use this SOP

Use this process **after**:

- A PR from `dev` → `main` has been **squash‑merged**
- CI is green
- You want `dev` and `main` to point to the **same commit**

---

### Preconditions

Run all commands from the repo root.

```bash
cd /Volumes/Dev/projects/omc-pipeline-poc
git status
```

Confirm:

- Working tree is clean
- You are on `dev`

Optional but recommended:

```bash
git fetch origin
```

---

### Safety step (non‑destructive backup)

Create a timestamped safety branch **before** resetting:

```bash
git branch dev-pre-reset-$(date +%Y%m%d-%H%M)
```

This is cheap insurance and costs nothing.

---

### Reset `dev` to match `main`

```bash
git reset --hard origin/main
```

At this point:

- `dev` HEAD == `main` HEAD
- Local history is clean

Verify:

```bash
git log -1 --oneline
```

---

### Force‑push `dev` safely

```bash
git push --force-with-lease origin dev
```

Why `--force-with-lease`?

- Prevents overwriting remote work you don’t have locally
- Safer than `--force`

---

### Post‑conditions (verify)

```bash
git fetch origin
git rev-parse dev main origin/dev origin/main
```

All hashes should be **identical**.

---

### Important rules (do not violate)

- ❌ Do **not** rebase `dev` after a squash merge
- ❌ Do **not** delete branches as part of this flow
- ✅ Always reset + force‑with‑lease
- ✅ Keep `dev` persistent and long‑lived

---

### Mental model

Think of `dev` as:

- A **working buffer**
- Periodically snapshotted into `main`
- Then **realigned** to `main` after squash

This keeps:

- PRs clean
- History readable
- No merge junk or rebases

---

### Summary

After every squash merge:

1. Backup branch (optional but recommended)
2. `git reset --hard origin/main`
3. `git push --force-with-lease origin dev`

This is the **official, repeatable, low‑risk** workflow we will continue using.
