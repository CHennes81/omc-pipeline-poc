#!/usr/bin/env python3
"""Rewrite every timestamp in db/seed.sql so the demo timeline reads like a real shoot.

Model (continuous camera-to-cloud flow, production in US Pacific, Jan = UTC-8; stored as UTC):
  * Capture slots keep the original shoot-day schedule, read as Pacific local clock time, then jittered
    by several minutes with random seconds (nothing lands on an even hour or half hour).
  * RAW upload to cloud storage completes 1-4 min after the take.
  * That triggers an automatic debayer/master transcode  (+9-16 min).
  * That triggers an automatic dailies transcode          (+7-14 min).   => ~20-33 min capture -> daily.
  * Edit exports land days later, in Pacific business hours; reworks 1-3 days after the export they revise.
  * Turnover and archive are single deliveries: package created, members added a few seconds apart,
    delivery events a few minutes later; archive follows turnover by hours.

Also renames the automated processing tools on the HDE_TRANSCODE / DAILIES_PUBLISHED events.

Deterministic (seeded per shot), so re-running gives the same result. Run BEFORE
rewrite_seed_omc_json.py (the OMC payloads read versions.created_at).

    python3 scripts/rewrite_seed_timeline.py            # writes db/seed.sql in place
    python3 scripts/rewrite_seed_timeline.py --check    # verify ordering constraints only
"""
import argparse
import importlib.util
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "db" / "seed.sql"

spec = importlib.util.spec_from_file_location("omcjson", ROOT / "scripts" / "rewrite_seed_omc_json.py")
omcjson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(omcjson)

PT = timedelta(hours=8)  # Pacific standard time offset (January)
SEED_STR = "exftr-timeline-v1"
MASTER_TOOL = "Cloud Auto-Debayer & Master Transcode"
DAILIES_TOOL = "Cloud Auto-Dailies Transcode"
PRODUCTION_CREATED = datetime(2026, 1, 12, 17, 3, 27, tzinfo=timezone.utc)
SLOTS = {  # original shoot schedule (clock time, read as Pacific local); fixed so re-runs are idempotent
    "011_001": "2026-01-15 08:00:00",
    "011_001A": "2026-01-15 08:15:00",
    "011_001B": "2026-01-15 08:30:00",
    "011_002": "2026-01-15 09:00:00",
    "011_003": "2026-01-15 09:30:00",
    "011_004": "2026-01-15 10:00:00",
    "012_001": "2026-01-15 11:00:00",
    "012_002": "2026-01-15 11:30:00",
    "012_003": "2026-01-15 12:00:00",
    "012_004": "2026-01-15 12:30:00",
    "013_001": "2026-01-15 14:00:00",
    "013_002": "2026-01-15 14:30:00",
    "013_003": "2026-01-15 15:00:00",
    "014_001": "2026-01-16 08:00:00",
    "014_002": "2026-01-16 08:30:00",
    "014_003": "2026-01-16 09:00:00",
    "014_004": "2026-01-16 09:30:00",
    "015_001": "2026-01-16 11:00:00",
    "015_002": "2026-01-16 11:30:00",
    "015_003": "2026-01-16 12:00:00",
    "015_004": "2026-01-16 12:30:00",
    "015_005": "2026-01-16 13:00:00",
    "016_001": "2026-01-16 14:00:00",
    "017_001": "2026-01-17 08:00:00",
    "018_002": "2026-01-17 11:30:00",
    "018_003": "2026-01-17 12:00:00",
    "019_001": "2026-01-17 14:00:00",
    "019_002": "2026-01-17 14:30:00",
}


def parse_ts(s):
    return datetime.strptime(s.replace("+00", ""), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def fmt(dt):
    return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}+00'::timestamptz"


def business_time(rng, day_local):
    """A random Pacific business-hours moment on `day_local` (a date at local midnight), returned as UTC."""
    secs = rng.randint(9 * 3600 + 7 * 60 + 13, 18 * 3600 + 41 * 60 + 47)
    return day_local + timedelta(seconds=secs) + PT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compute and verify only; do not write")
    args = ap.parse_args()

    text = SEED.read_text()
    lines, tables = omcjson.parse_seed(text)
    R = lambda name: omcjson.rows_as_dicts(tables, name)

    shots = R("shots")
    assets = {r["id"]: r for _, r, _, _ in R("assets")}
    shot_idx = {r["id"]: i for i, (_, r, _, _) in enumerate(shots)}
    vrows = R("versions")
    versions = {r["id"]: r for _, r, _, _ in vrows}

    # ---- per-shot timeline
    T = {}  # version_id -> created_at ; ("cap", shot_id) -> capture time
    prev_t0 = None
    for _, s, _, _ in shots:
        rng = random.Random(f"{SEED_STR}-{s['shot_code']}")
        i = shot_idx[s["id"]]
        slot = parse_ts(SLOTS[s["shot_code"]])  # original schedule, read as Pacific local clock time
        t0 = slot + PT + timedelta(seconds=rng.randint(-7 * 60 - 21, 9 * 60 + 38))
        if prev_t0 is not None and t0 < prev_t0 + timedelta(minutes=7):  # takes stay chronological
            t0 = prev_t0 + timedelta(seconds=rng.randint(7 * 60 + 9, 14 * 60 + 44))
        prev_t0 = t0
        T[("cap", s["id"])] = t0
        raw = t0 + timedelta(seconds=rng.randint(64, 233))
        master = raw + timedelta(seconds=rng.randint(9 * 60 + 4, 15 * 60 + 57))
        daily = master + timedelta(seconds=rng.randint(7 * 60 + 11, 13 * 60 + 49))
        T[("stage", s["id"], "CAMERA_ORIGINAL")] = raw
        T[("stage", s["id"], "HDE_MASTER")] = master
        T[("stage", s["id"], "DAILIES_PROXY")] = daily
        local_midnight = (t0 - PT).replace(hour=0, minute=0, second=0, microsecond=0)
        if i < 24:  # last 4 shots have no edit export (blocked)
            T[("stage", s["id"], "EDIT_EXPORT")] = business_time(rng, local_midnight + timedelta(days=2 + i % 4))

    # version_id -> time
    for _, v, _, _ in vrows:
        shot_id = None
        a = assets[v["asset_id"]]
        shot_id = a["shot_id"]
        vt = v["version_type"]
        is_rework = bool(v.get("creative_context"))
        if not is_rework:
            T[v["id"]] = T[("stage", shot_id, vt)]
    for _, v, _, _ in vrows:  # reworks after their source export
        if v.get("creative_context"):
            rng = random.Random(f"{SEED_STR}-rework-{v['id']}")
            src = T[v["derived_from_version_id"]]
            day = (src - PT).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=rng.randint(1, 3))
            T[v["id"]] = business_time(rng, day)

    # ---- packages
    pk_rows = R("packages")
    pm_rows = R("package_members")
    ev_rows = R("events")
    pkg_type = {r["id"]: r["package_type"] for _, r, _, _ in pk_rows}
    turnover_id = next(i for i, t in pkg_type.items() if t == "TURNOVER")
    archive_id = next(i for i, t in pkg_type.items() if t == "ARCHIVE")
    rng = random.Random(f"{SEED_STR}-packages")
    t_members_max = max(T[r["version_id"]] for _, r, _, _ in pm_rows if r["package_id"] == turnover_id)
    T[("pkg", turnover_id)] = t_members_max + timedelta(seconds=rng.randint(95 * 60 + 11, 230 * 60 + 53))
    archive_after = T[("pkg", turnover_id)] + timedelta(minutes=30)
    # archive follows turnover (and every shot's turnover event) by hours
    T[("pkg", archive_id)] = archive_after + timedelta(seconds=rng.randint(3 * 3600 + 17 * 60, 20 * 3600 + 49 * 60))

    # ---- build edits: (line_no, column, new_token)
    edits = []

    def put(ln, cols, toks, col, value):
        s, e, _ = toks[cols.index(col)]
        edits.append((ln, s, e, value))

    prod_line = next(i for i, l in enumerate(lines) if l.startswith("VALUES ('550e8400-e29b-41d4-a716-446655440000', 'EXFTR'"))
    import re as _re
    lines[prod_line] = _re.sub(r"'[0-9: +-]+'::timestamptz", fmt(PRODUCTION_CREATED), lines[prod_line])
    for ln, r, cols, toks in shots:
        put(ln, cols, toks, "created_at", fmt(T[("cap", r["id"])]))
    for ln, r, cols, toks in R("assets"):
        put(ln, cols, toks, "created_at", fmt(T[("stage", r["shot_id"], "CAMERA_ORIGINAL")]))
    for ln, r, cols, toks in vrows:
        put(ln, cols, toks, "created_at", fmt(T[r["id"]]))
    for ln, r, cols, toks in R("version_lineage"):
        put(ln, cols, toks, "created_at", fmt(T[r["derived_version_id"]]))
    for ln, r, cols, toks in pk_rows:
        put(ln, cols, toks, "created_at", fmt(T[("pkg", r["id"])]))
    seq = {}
    for ln, r, cols, toks in pm_rows:
        k = seq.get(r["package_id"], 0)
        seq[r["package_id"]] = k + 1
        off = sum(random.Random(f"{SEED_STR}-member-{r['package_id']}-{j}").randint(1, 5) for j in range(k + 1))
        put(ln, cols, toks, "created_at", fmt(T[("pkg", r["package_id"])] + timedelta(seconds=off)))
    ev_seq = {}
    event_times = []  # (shot_id, type, time) for --check
    for ln, r, cols, toks in ev_rows:
        et = r["event_type"]
        if et == "CAPTURE":
            t = T[("cap", r["shot_id"])]
        elif et in ("HDE_TRANSCODE", "DAILIES_PUBLISHED", "EDIT_EXPORT_CREATED"):
            t = T[r["version_id"]]
            if et == "HDE_TRANSCODE":
                put(ln, cols, toks, "tool", f"'{MASTER_TOOL}'")
            elif et == "DAILIES_PUBLISHED":
                put(ln, cols, toks, "tool", f"'{DAILIES_TOOL}'")
        elif et in ("TURNOVER_DELIVERED", "ARCHIVED"):
            pid = r["package_id"]
            k = ev_seq.get(pid, 0)
            ev_seq[pid] = k + 1
            base = T[("pkg", pid)] + timedelta(seconds=180 + random.Random(f"{SEED_STR}-evbase-{pid}").randint(0, 420))
            off = sum(random.Random(f"{SEED_STR}-ev-{pid}-{j}").randint(1, 4) for j in range(k + 1))
            t = base + timedelta(seconds=off)
        else:
            raise SystemExit(f"unhandled event type {et}")
        event_times.append((r["shot_id"], et, t))
        put(ln, cols, toks, "created_at", fmt(t))

    # ---- verify ordering constraints
    errs = []
    by_shot = {}
    for sid, et, t in event_times:
        by_shot.setdefault(sid, {}).setdefault(et, []).append(t)
    order = ["CAPTURE", "HDE_TRANSCODE", "DAILIES_PUBLISHED", "EDIT_EXPORT_CREATED", "TURNOVER_DELIVERED", "ARCHIVED"]
    chain_minutes = []
    for sid, d in by_shot.items():
        prev = None
        for et in order:
            if et in d:
                t = min(d[et]) if et != "EDIT_EXPORT_CREATED" else min(d[et])
                if prev and t <= prev[1]:
                    errs.append(f"{sid}: {et} {t} not after {prev[0]} {prev[1]}")
                prev = (et, t)
        if "CAPTURE" in d and "DAILIES_PUBLISHED" in d:
            chain_minutes.append((d["DAILIES_PUBLISHED"][0] - d["CAPTURE"][0]).total_seconds() / 60)
    for _, v, _, _ in vrows:
        if v.get("derived_from_version_id") and T[v["id"]] <= T[v["derived_from_version_id"]]:
            errs.append(f"version {v['id']} not after its source")
    allt = [x for x in T.values() if isinstance(x, datetime)]
    even = sum(1 for t in allt if t.minute == 0 and t.second == 0)
    print(f"timestamps assigned: {len(allt)}; on an exact hour: {even}")
    print(f"capture->daily minutes: min {min(chain_minutes):.1f} / max {max(chain_minutes):.1f} / avg {sum(chain_minutes)/len(chain_minutes):.1f}")
    print(f"turnover {T[('pkg', turnover_id)]:%Y-%m-%d %H:%M:%S}Z  archive {T[('pkg', archive_id)]:%Y-%m-%d %H:%M:%S}Z")
    if errs:
        print("ORDER ERRORS:"); [print(" ", e) for e in errs[:20]]
        return 1
    print("ordering constraints OK")
    if args.check:
        return 0

    for ln, s, e, value in sorted(edits, key=lambda x: (x[0], -x[1])):
        lines[ln] = lines[ln][:s] + value + lines[ln][e:]
    SEED.write_text("\n".join(lines))
    print(f"rewrote {len(edits)} values in {SEED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
