"""Every Audit Information card on the Ask page must carry a real value for every field its card type shows.

Needs the seeded database (skips itself when none is reachable). It runs each Ask template that returns version
evidence for every shot / package and checks the rows the VersionAuditCard renders.

Card types (see Documentation/Ask-Audit-Card-Design.md):
  CAMERA_ORIGINAL            Camera, Format, Lens, Reel + Timecode, Captured By, Locator + Version ID
  CAMERA_MASTER, DAILIES_PROXY   Format, Source, Timecode, Created By, Locator + Version ID
  EDIT_EXPORT                Format, Timecode, Reason, Delivered in, Created By, Locator + Version ID
A field that a type cannot carry stays empty (the card shows a hyphen).
"""
import pytest
from sqlalchemy import text

from app import ask_templates as T
from app.database import SessionLocal

COMMON = ["id", "version_type", "storage_uri", "created_at", "codec", "container", "fps", "width", "height",
          "color_space", "timecode_in", "timecode_out", "created_by_actor", "created_by_tool"]
CAMERA_ONLY = ["reel", "clip_name", "camera_make", "camera_model", "camera_serial", "exposure_index",
               "lens_make", "lens_model", "focal_length", "t_stop"]
SOURCE = ["source_reel", "source_clip_name"]


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    try:
        session.execute(text("SELECT 1 FROM versions LIMIT 1"))
    except Exception:
        session.close()
        pytest.skip("no seeded database reachable")
    yield session
    session.close()


def _all_version_rows(db):
    prod = "EXFTR"
    shots = [r[0] for r in db.execute(text("SELECT shot_code FROM shots")).fetchall()]
    pkgs = [str(r[0]) for r in db.execute(text("SELECT id FROM packages")).fetchall()]
    assert shots and pkgs, "database is not seeded"
    for shot in shots:
        for fn in (T.latest_camera_original, T.lineage_chain_to_latest_edit_export,
                   T.source_relink_keys, T.latest_versions_by_type):
            for row in fn(db, shot, prod)["evidence"]["versions"]:
                yield fn.__name__, shot, row
    for pid in pkgs:
        for row in T.package_members(db, pid, prod)["evidence"]["versions"]:
            yield "package_members", pid, row


def _empty(value):
    return value in (None, "")


def test_every_card_field_is_populated_per_type(db):
    problems, seen, rework_reasons = [], 0, 0
    for source, where, row in _all_version_rows(db):
        seen += 1
        vt = row["version_type"]
        ctx = (source, where, vt)
        for key in COMMON:
            if _empty(row.get(key)):
                problems.append((*ctx, key, "missing"))
        for key in CAMERA_ONLY:
            if vt == "CAMERA_ORIGINAL" and _empty(row.get(key)):
                problems.append((*ctx, key, "missing"))
            if vt != "CAMERA_ORIGINAL" and not _empty(row.get(key)):
                problems.append((*ctx, key, "unexpected"))
        for key in SOURCE:
            if vt == "CAMERA_ORIGINAL" and not _empty(row.get(key)):
                problems.append((*ctx, key, "unexpected"))
            if vt != "CAMERA_ORIGINAL" and _empty(row.get(key)):
                problems.append((*ctx, key, "missing"))
        if vt == "EDIT_EXPORT":
            if not isinstance(row.get("delivered_in"), list):
                problems.append((*ctx, "delivered_in", "not a list"))
            rework_reasons += 0 if _empty(row.get("reason")) else 1
        elif not _empty(row.get("reason")):
            problems.append((*ctx, "reason", "unexpected"))
    assert seen > 100, f"only {seen} cards checked"
    assert not problems, problems[:10]


def test_reason_present_exactly_for_reworks(db):
    rows = db.execute(text("""
        SELECT v.id, v.creative_context IS NOT NULL AS is_rework FROM versions v
        WHERE v.version_type = 'EDIT_EXPORT'""")).fetchall()
    rework_ids = {str(r[0]) for r in rows if r[1]}
    assert len(rework_ids) == 4
    for shot in [r[0] for r in db.execute(text("SELECT shot_code FROM shots")).fetchall()]:
        for row in T.lineage_chain_to_latest_edit_export(db, shot, "EXFTR")["evidence"]["versions"]:
            if row["version_type"] == "EDIT_EXPORT":
                assert _empty(row["reason"]) == (str(row["id"]) not in rework_ids), (shot, row["id"])


def test_edit_export_codec_follows_the_editing_tool(db):
    seen = set()
    for shot in [r[0] for r in db.execute(text("SELECT shot_code FROM shots")).fetchall()]:
        for row in T.lineage_chain_to_latest_edit_export(db, shot, "EXFTR")["evidence"]["versions"]:
            if row["version_type"] == "EDIT_EXPORT":
                avid = row["created_by_tool"] == "Avid Media Composer"
                assert row["codec"] == ("DNxHR HQX" if avid else "ProRes 422"), (shot, row["created_by_tool"], row["codec"])
                seen.add(row["codec"])
    assert seen == {"DNxHR HQX", "ProRes 422"}


def test_delivered_in_matches_package_membership(db):
    expected = db.execute(text("SELECT COUNT(*) FROM package_members")).scalar()
    got = 0
    for pid in [str(r[0]) for r in db.execute(text("SELECT id FROM packages")).fetchall()]:
        got += len(T.package_members(db, pid, "EXFTR")["evidence"]["versions"])
    assert got == expected


def test_relink_card_also_carries_the_clip_name(db):
    row = T.source_relink_keys(db, "011_001", "EXFTR")["evidence"]["versions"][0]
    assert row["clip_name"] and row["reel"] == "A001" and row["version_type"] == "CAMERA_ORIGINAL"
