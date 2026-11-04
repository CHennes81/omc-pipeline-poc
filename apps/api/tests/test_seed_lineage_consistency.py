"""Guard against drift between the two places lineage is stored.

Lineage lives twice by design:
  * SQL:  versions.derived_from_version_id (+ the version_lineage table) -- used by the fast recursive queries.
  * JSON: versions.omc_json -> version.DerivationOf / RevisionOf        -- the interoperable OMC record.

Neo4j would need only one; with SQL we keep both and this test makes sure they can never disagree.
It reads db/seed.sql directly (the source of truth for seed data), so it needs no database.
"""
import importlib.util
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEED = Path(os.environ.get("SEED_SQL", ROOT / "db" / "seed.sql"))  # override lets a test run target a corrupted copy

_spec = importlib.util.spec_from_file_location("seed_parser", ROOT / "scripts" / "rewrite_seed_omc_json.py")
_seed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_seed)

VERSION_TYPES = {"CAMERA_ORIGINAL", "CAMERA_MASTER", "DAILIES_PROXY", "EDIT_EXPORT"}


def _load():
    _, tables = _seed.parse_seed(SEED.read_text())
    versions = [r for _, r, _, _ in _seed.rows_as_dicts(tables, "versions")]
    lineage = [r for _, r, _, _ in _seed.rows_as_dicts(tables, "version_lineage")]
    return versions, lineage


def _payload(v):
    return json.loads(v["omc_json"])


def _parent_version_id(payload):
    """Version id referenced by version.DerivationOf / RevisionOf, and which of the two it was."""
    ver = payload.get("version") or {}
    for key in ("DerivationOf", "RevisionOf"):
        if key in ver:
            value = ver[key]["identifier"][0]["identifierValue"]
            return key, value.rsplit("/version/", 1)[1]
    return None, None


def test_seed_has_expected_shape():
    versions, _ = _load()
    assert len(versions) == 112
    assert {v["version_type"] for v in versions} == VERSION_TYPES


def test_json_parent_matches_sql_column():
    versions, _ = _load()
    mismatches = []
    for v in versions:
        sql_parent = v.get("derived_from_version_id")
        sql_parent = None if sql_parent in (None, "NULL") else sql_parent
        _, json_parent = _parent_version_id(_payload(v))
        if sql_parent != json_parent:
            mismatches.append((v["id"], sql_parent, json_parent))
    assert not mismatches, f"SQL derived_from_version_id and OMC JSON parent disagree: {mismatches[:5]}"


def test_relationship_kind_matches_rework():
    """Rework exports are RevisionOf their source export; every other derived version is DerivationOf."""
    versions, _ = _load()
    wrong = []
    for v in versions:
        kind, _ = _parent_version_id(_payload(v))
        is_rework = bool(v.get("creative_context"))
        expected = "RevisionOf" if is_rework else ("DerivationOf" if v.get("derived_from_version_id") not in (None, "NULL") else None)
        if kind != expected:
            wrong.append((v["id"], kind, expected))
    assert not wrong, wrong[:5]


def test_version_lineage_table_matches_versions():
    versions, lineage = _load()
    from_versions = {(v["id"], v["derived_from_version_id"]) for v in versions if v.get("derived_from_version_id") not in (None, "NULL")}
    from_table = {(r["derived_version_id"], r["source_version_id"]) for r in lineage}
    assert from_table == from_versions


def test_payload_identifiers_match_row_ids():
    versions, _ = _load()
    bad = []
    for v in versions:
        p = _payload(v)
        if p["identifier"][0]["identifierValue"] != f"asset/{v['asset_id']}/version/{v['id']}":
            bad.append((v["id"], "Asset identifier"))
        if p["AssetSC"]["identifier"][0]["identifierValue"] != f"assetsc/{v['id']}":
            bad.append((v["id"], "AssetSC identifier"))
    assert not bad, bad[:5]


def test_payload_matches_sql_columns_phase_a():
    """Until the duplicated columns are dropped, the JSON must agree with them (codec, file name, frame rate)."""
    versions, _ = _load()
    bad = []
    for v in versions:
        sc = _payload(v)["AssetSC"]
        sp = sc["structuralProperties"]
        custom = sc["customData"][0]["value"]
        if sp["codec"] != v["codec"]:
            bad.append((v["id"], "codec"))
        if sp["fileDetails"]["filePath"] != v["storage_uri"]:
            bad.append((v["id"], "storage_uri"))
        if custom["container"] != v["container"]:
            bad.append((v["id"], "container"))
        if float(custom["frameRate"]) != float(v["fps"]):
            bad.append((v["id"], "fps"))
    assert not bad, bad[:5]


def test_seed_has_no_json_colon_digit_pattern():
    """SQLAlchemy text() reads `:24` in the SQL text as a bind parameter; seed JSON must not contain `\":<digit>`."""
    assert not re.search(r'":[0-9]', SEED.read_text())


def test_instanceinfo_date_matches_provenance_timestamp():
    """instanceInfo.createdOn can only hold a plain date (OMC schema quirk); it must be the date of provenance.createdOn."""
    versions, _ = _load()
    bad = []
    for v in versions:
        p = _payload(v)
        d, ts = p["instanceInfo"]["createdOn"], p["provenance"]["createdOn"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) or not ts.startswith(d + "T"):
            bad.append((v["id"], d, ts))
    assert not bad, bad[:5]
