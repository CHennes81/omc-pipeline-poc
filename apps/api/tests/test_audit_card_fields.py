"""Every Audit Information card on the Ask page must show a real value for every field it can carry.

Needs the seeded database (skips itself when none is reachable). It runs each Ask template that returns version
evidence for every shot / package and checks the rows the VersionAuditCard would render.

Card fields: Version Type, Created, Codec, FPS, Timecode In/Out, Reel, Version ID, Locator (storage_uri).
`reel` is camera metadata, so it is required for CAMERA_ORIGINAL and expected to be empty for every other type.
"""
import pytest
from sqlalchemy import text

from app import ask_templates as T
from app.database import SessionLocal

ALWAYS = ["id", "version_type", "storage_uri", "created_at", "codec", "fps", "timecode_in", "timecode_out"]


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


def test_every_card_field_is_populated(db):
    problems, seen = [], 0
    for source, where, row in _all_version_rows(db):
        seen += 1
        for key in ALWAYS:
            if row.get(key) in (None, ""):
                problems.append((source, where, row.get("version_type"), key, "missing"))
        has_reel = bool(row.get("reel"))
        if row.get("version_type") == "CAMERA_ORIGINAL" and not has_reel:
            problems.append((source, where, "CAMERA_ORIGINAL", "reel", "missing"))
        if row.get("version_type") != "CAMERA_ORIGINAL" and has_reel:
            problems.append((source, where, row.get("version_type"), "reel", "unexpected"))
    assert seen > 100, f"only {seen} cards checked"
    assert not problems, problems[:10]


def test_relink_card_also_carries_the_clip_name(db):
    row = T.source_relink_keys(db, "011_001", "EXFTR")["evidence"]["versions"][0]
    assert row["clip_name"] and row["reel"] == "A001" and row["version_type"] == "CAMERA_ORIGINAL"
