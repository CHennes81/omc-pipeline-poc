#!/usr/bin/env python3
"""Upgrade a hosted (or local) Postgres to the current schema and demo data, in ONE transaction.

Why this exists: the API never changes the schema itself, and `psql` is not assumed to be installed. This runs the
same SQL files with psycopg2 (already in apps/api/.venv). The demo database is read-only reference data, so the
upgrade is "migrate, re-create views, truncate, reload seed, verify". Any failure rolls everything back.

Steps (--apply):
  1. db/migrations/*.sql   in name order (idempotent: DROP COLUMN IF EXISTS ...)
  2. db/views.sql          CREATE OR REPLACE VIEW
  3. db/seed.sql           TRUNCATEs every table, then loads the seed
  4. checks                expected row counts + the integrity / lineage queries in db/seed_verify.sql (must be 0)
  Commit only if every check passes.

Credentials are NEVER printed (only host:port/db). Three ways to supply them:
  --url-file PATH / --url-env NAME   a full postgresql:// URL
  --pg-env --host H --port P         user, password and database from PGUSER / PGPASSWORD / PGDATABASE, e.g. injected by
                                     `railway run --service Postgres ...` while `railway connect Postgres --tunnel-only`
                                     is open in another terminal (host 127.0.0.1, port = the tunnel's local port)

Usage (from the repo root, with the API venv):
    apps/api/.venv/bin/python scripts/upgrade_db.py --url-file PATH               # read-only inspection (default)
    apps/api/.venv/bin/python scripts/upgrade_db.py --url-file PATH --apply --expect-host HOST

    --url-env NAME     read the URL from this environment variable instead of --url-file
    --pg-env           build the connection from PGUSER / PGPASSWORD / PGDATABASE plus --host and --port
    --expect-port P    required with --apply when the host is local (a tunnel), to tell it apart from a dev database
    --expect-host H    required with --apply; must equal the target's host (guards against the wrong database)
    --allow-local      permit localhost / 127.0.0.1 targets (otherwise refused, to avoid wiping a dev DB by accident)
"""
import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {"productions": 1, "shots": 28, "assets": 28, "versions": 112, "packages": 2}


def load_params(args):
    """Return psycopg2 connect kwargs."""
    if args.pg_env:
        need = ["PGUSER", "PGPASSWORD", "PGDATABASE"]
        missing = [k for k in need if not os.environ.get(k)]
        if missing or not args.host or not args.port:
            sys.exit(f"--pg-env needs --host, --port and env vars {need} (missing: {missing})")
        return {"host": args.host, "port": args.port, "user": os.environ["PGUSER"],
                "password": os.environ["PGPASSWORD"], "dbname": os.environ["PGDATABASE"]}
    u = urlparse(load_url(args))
    return {"host": u.hostname, "port": u.port or 5432, "user": u.username, "password": u.password,
            "dbname": (u.path or "/").lstrip("/")}


def load_url(args):
    if args.url_file:
        url = Path(args.url_file).expanduser().read_text().strip()
    elif args.url_env:
        url = os.environ.get(args.url_env, "").strip()
    else:
        sys.exit("give --url-file PATH, --url-env NAME, or --pg-env")
    if not url:
        sys.exit("connection URL is empty")
    return url.replace("postgres://", "postgresql://", 1)


def describe(p):
    return p["host"] or "?", f"{p['host']}:{p['port']}/{p['dbname']}"


def split_statements(sql):
    """Split a verification file on ';' (the file has no semicolons inside strings or comments)."""
    body = "\n".join(line for line in sql.splitlines() if not line.strip().startswith("--"))
    return [s.strip() for s in body.split(";") if s.strip()]


def q(cur, sql):
    cur.execute(sql)
    return cur.fetchall()


def inspect(cur):
    print("\n-- versions columns:", ", ".join(r[0] for r in q(cur, "SELECT column_name FROM information_schema.columns WHERE table_name='versions' ORDER BY ordinal_position")))
    print("-- assets columns:  ", ", ".join(r[0] for r in q(cur, "SELECT column_name FROM information_schema.columns WHERE table_name='assets' ORDER BY ordinal_position")))
    for t in ("productions", "shots", "assets", "versions", "version_lineage", "events", "packages", "package_members"):
        try:
            print(f"-- {t}: {q(cur, f'SELECT COUNT(*) FROM {t}')[0][0]} rows")
        except psycopg2.Error as e:
            cur.connection.rollback()
            print(f"-- {t}: unreadable ({str(e).splitlines()[0]})")
    try:
        print("-- event types:", dict(q(cur, "SELECT event_type, COUNT(*) FROM events GROUP BY 1 ORDER BY 1")))
        print("-- version types:", dict(q(cur, "SELECT version_type, COUNT(*) FROM versions GROUP BY 1 ORDER BY 1")))
        print("-- shot stages:", dict(q(cur, "SELECT stage, COUNT(*) FROM v_shot_stage GROUP BY 1 ORDER BY 1")))
    except psycopg2.Error as e:
        cur.connection.rollback()
        print("-- stage summary unavailable:", str(e).splitlines()[0])


def apply(cur):
    for f in sorted((ROOT / "db" / "migrations").glob("*.sql")):
        print(f"-- applying {f.relative_to(ROOT)}")
        cur.execute(f.read_text())
    print("-- applying db/views.sql")
    cur.execute((ROOT / "db" / "views.sql").read_text())
    print("-- loading db/seed.sql (truncates every table first)")
    cur.execute((ROOT / "db" / "seed.sql").read_text())

    failures = []
    for table, n in EXPECTED.items():
        got = q(cur, f"SELECT COUNT(*) FROM {table}")[0][0]
        print(f"-- check {table}: {got} (expected {n})")
        if got != n:
            failures.append(f"{table}: {got} != {n}")
    for stmt in split_statements((ROOT / "db" / "seed_verify.sql").read_text()):
        rows = q(cur, stmt)
        if rows and len(rows[0]) == 2 and re.search(r"(violations|mismatch)", stmt, re.I):
            for name, n in rows:
                print(f"-- check {name}: {n} violations")
                if n != 0:
                    failures.append(f"{name}: {n}")
    for col in ("codec", "container", "fps", "timecode_in", "timecode_out", "bitrate"):
        if q(cur, f"SELECT 1 FROM information_schema.columns WHERE table_name='versions' AND column_name='{col}'"):
            failures.append(f"versions.{col} still exists")
    for col in ("clip_name", "reel_or_roll", "camera_serial"):
        if q(cur, f"SELECT 1 FROM information_schema.columns WHERE table_name='assets' AND column_name='{col}'"):
            failures.append(f"assets.{col} still exists")
    print("-- shot stages:", dict(q(cur, "SELECT stage, COUNT(*) FROM v_shot_stage GROUP BY 1 ORDER BY 1")))
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url-file")
    ap.add_argument("--url-env")
    ap.add_argument("--pg-env", action="store_true")
    ap.add_argument("--host")
    ap.add_argument("--port", type=int)
    ap.add_argument("--expect-port", type=int)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--expect-host")
    ap.add_argument("--allow-local", action="store_true")
    args = ap.parse_args()

    params = load_params(args)
    host, label = describe(params)
    print(f"target: {label}")
    is_local = host in ("localhost", "127.0.0.1", "::1")
    if is_local and not args.allow_local:
        sys.exit("refusing a local target without --allow-local")
    if args.apply and args.expect_host != host:
        sys.exit(f"--apply needs --expect-host {host} (got {args.expect_host!r}); nothing was changed")
    if args.apply and is_local and args.expect_port != params["port"]:
        sys.exit(f"--apply on a local target needs --expect-port {params['port']}; nothing was changed")

    try:
        conn = psycopg2.connect(connect_timeout=20, **params)
    except psycopg2.OperationalError as e:
        sys.exit(f"could not connect to {label}: {str(e).strip().splitlines()[-1]}")
    try:
        cur = conn.cursor()
        if not args.apply:
            conn.set_session(readonly=True)
            print("mode: INSPECT (read-only)")
            inspect(cur)
            return 0
        print("mode: APPLY (single transaction)")
        print("\n== before ==")
        inspect(cur)
        failures = apply(cur)
        if failures:
            conn.rollback()
            print("\nFAILED, rolled back, nothing changed:", *failures, sep="\n  - ")
            return 1
        conn.commit()
        print("\nCOMMITTED. Upgrade complete.")
        return 0
    except Exception as e:
        conn.rollback()
        print("\nERROR, rolled back, nothing changed:", str(e).splitlines()[0])
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
