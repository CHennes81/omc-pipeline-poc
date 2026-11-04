"""omc_fields: media attributes read from the OMC-JSON payload (Phase B replaced the duplicated columns)."""
import importlib.util
import json
import os
import re
from pathlib import Path

from app import omc_fields as f

ROOT = Path(__file__).resolve().parents[3]
SEED = Path(os.environ.get("SEED_SQL", ROOT / "db" / "seed.sql"))
_spec = importlib.util.spec_from_file_location("seed_parser", ROOT / "scripts" / "rewrite_seed_omc_json.py")
_seed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_seed)


def _versions():
    _, tables = _seed.parse_seed(SEED.read_text())
    return [r for _, r, _, _ in _seed.rows_as_dicts(tables, "versions")]


def test_every_version_yields_media_fields():
    for v in _versions():
        p = json.loads(v["omc_json"])
        assert f.codec(p) and f.container(p)
        assert f.fps(p) == 24.0
        assert f.timecode_in(p) == "01:00:00:00" and f.timecode_out(p) == "01:00:15:00"


def test_camera_original_attributes():
    cams = [json.loads(v["omc_json"]) for v in _versions() if v["version_type"] == "CAMERA_ORIGINAL"]
    assert len(cams) == 28
    for p in cams:
        assert re.fullmatch(r"A\d{3}C\d{3}_\d{3}_\d{3}[A-Z]?\.mxf", f.clip_name(p))
        assert re.fullmatch(r"A\d{3}", f.reel(p)) and f.clip_name(p).startswith(f.reel(p))  # reel is the clip's prefix
        assert f.camera_serial(p) == "ALX-001234"
        assert f.codec(p) == "ARRIRAW" and f.container(p) == "MXF"


def test_non_camera_stages_use_timing_for_timecode():
    for v in _versions():
        if v["version_type"] != "CAMERA_ORIGINAL":
            p = json.loads(v["omc_json"])
            assert f.timecode_in(p) == p["assetFC"]["functionalProperties"]["timing"]["sourceStart"]
            assert f.clip_name(p) is None and f.reel(p) is None


def test_missing_or_empty_payload_is_none_not_error():
    for p in (None, {}, {"AssetSC": {}}):
        assert f.codec(p) is None and f.fps(p) is None and f.timecode_in(p) is None and f.clip_name(p) is None


def test_sql_fragments_use_only_constant_paths():
    for sql in (f.SQL_CODEC, f.SQL_FPS, f.SQL_TIMECODE_IN, f.SQL_CLIP_NAME, f.SQL_REEL, f.SQL_CAMERA_SERIAL):
        assert "v.omc_json" in sql and ":" not in sql.replace("::numeric(10,2)", "")  # no bind-param lookalikes
