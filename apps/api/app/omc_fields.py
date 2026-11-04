"""Media attributes read from a version's OMC-JSON payload (`versions.omc_json`).

Phase B removed the relational columns that duplicated the JSON (versions.codec / container / fps / timecode_in /
timecode_out / bitrate, assets.clip_name / reel_or_roll / camera_serial). The OMC-JSON `Asset` is now the only place
these live. Two views of the same paths are provided and must stay in step (tests/test_omc_fields.py checks them
against each other and against the seed):

  * Python extractors, used by the ORM (`models.Version` properties) and the REST responses.
  * SQL expressions over a `versions` row aliased `v`, used by the Ask templates' raw SQL.

Paths (OMC-JSON v2.8; OMC has no native frame rate / container / clip name field, so those three sit in the
`AssetSC.customData` entry with domain "poc", namespace "plc"):

  codec        AssetSC.structuralProperties.codec
  container    AssetSC.customData[poc/plc].value.container
  fps          AssetSC.customData[poc/plc].value.frameRate            (string in JSON, numeric here)
  timecode in  assetFC.functionalProperties.cameraMetadata.timecodeStart  (camera original)
               or assetFC.functionalProperties.timing.sourceStart         (every other stage)
  timecode out ...cameraMetadata.timecodeEnd / ...timing.sourceEnd
  clip name    AssetSC.customData[poc/plc].value.clipName            (camera original only)
  reel         assetFC.functionalProperties.cameraMetadata.reelName  (camera original only)
  camera serial assetFC.functionalProperties.cameraMetadata.cameraSerialNumber (camera original only)
"""
from typing import Any, Dict, Optional

CUSTOM_DOMAIN, CUSTOM_NAMESPACE = "poc", "plc"


def _get(obj: Any, *path: str) -> Any:
    for key in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _custom(omc: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """The poc/plc customData value of the AssetSC (empty dict if absent)."""
    for entry in _get(omc, "AssetSC", "customData") or []:
        if entry.get("domain") == CUSTOM_DOMAIN and entry.get("namespace") == CUSTOM_NAMESPACE:
            return entry.get("value") or {}
    return {}


def _fprops(omc: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return _get(omc, "assetFC", "functionalProperties") or {}


def codec(omc): return _get(omc, "AssetSC", "structuralProperties", "codec")
def container(omc): return _custom(omc).get("container")


def fps(omc) -> Optional[float]:
    value = _custom(omc).get("frameRate")
    return float(value) if value not in (None, "") else None


def timecode_in(omc):
    f = _fprops(omc)
    return _get(f, "cameraMetadata", "timecodeStart") or _get(f, "timing", "sourceStart")


def timecode_out(omc):
    f = _fprops(omc)
    return _get(f, "cameraMetadata", "timecodeEnd") or _get(f, "timing", "sourceEnd")


def clip_name(omc): return _custom(omc).get("clipName")
def reel(omc): return _get(_fprops(omc), "cameraMetadata", "reelName")
def camera_serial(omc): return _get(_fprops(omc), "cameraMetadata", "cameraSerialNumber")


# ---- SQL equivalents (alias the versions table as `v`). Constants only: never interpolate user input. ----
_FP = "v.omc_json->'assetFC'->'functionalProperties'"
_CUSTOM = "v.omc_json->'AssetSC'->'customData'->0->'value'"  # the single poc/plc entry (the seed writes exactly one)

SQL_CODEC = "v.omc_json->'AssetSC'->'structuralProperties'->>'codec'"
SQL_CONTAINER = f"{_CUSTOM}->>'container'"
SQL_FPS = f"({_CUSTOM}->>'frameRate')::numeric(10,2)"
SQL_TIMECODE_IN = f"COALESCE({_FP}->'cameraMetadata'->>'timecodeStart', {_FP}->'timing'->>'sourceStart')"
SQL_TIMECODE_OUT = f"COALESCE({_FP}->'cameraMetadata'->>'timecodeEnd', {_FP}->'timing'->>'sourceEnd')"
SQL_CLIP_NAME = f"{_CUSTOM}->>'clipName'"
SQL_REEL = f"{_FP}->'cameraMetadata'->>'reelName'"
SQL_CAMERA_SERIAL = f"{_FP}->'cameraMetadata'->>'cameraSerialNumber'"
