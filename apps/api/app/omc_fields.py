"""Media attributes read from a version's OMC-JSON payload (`versions.omc_json`).

Phase B removed the relational columns that duplicated the JSON (versions.codec / container / fps / timecode_in /
timecode_out / bitrate, assets.clip_name / reel_or_roll / camera_serial). The OMC-JSON `Asset` is now the only place
these live. Two views of the same paths are provided and must stay in step (tests/test_omc_fields.py checks them
against each other and against the seed):

  * Python extractors, used by the ORM (`models.Version` properties) and the REST responses.
  * SQL expressions over a `versions` row aliased `v`, used by the Ask templates' raw SQL.

Paths (OMC-JSON v2.8). The schema defines no frame rate, container or clip name property. Frame rate and container sit
in the `AssetSC.customData` entry with domain "poc", namespace "plc". Clip name sits in `assetFC.functionalProperties`,
where MovieLabs' own HSM examples put it (the validator does not check unknown keys there):

  codec        AssetSC.structuralProperties.codec
  container    AssetSC.customData[poc/plc].value.container
  fps          AssetSC.customData[poc/plc].value.frameRate            (string in JSON, numeric here)
  timecode in  assetFC.functionalProperties.cameraMetadata.timecodeStart  (camera original)
               or assetFC.functionalProperties.timing.sourceStart         (every other stage)
  timecode out ...cameraMetadata.timecodeEnd / ...timing.sourceEnd
  clip name    assetFC.functionalProperties.clipName                 (camera original only)
  reel         assetFC.functionalProperties.cameraMetadata.reelName  (camera original only)
  camera serial assetFC.functionalProperties.cameraMetadata.cameraSerialNumber (camera original only)
  width/height AssetSC.structuralProperties.dimensions.width/height ("3840px" -> "3840")
  colour space AssetSC.customData[poc/plc].value.colorSpace
  camera/lens  assetFC.functionalProperties.cameraMetadata.* / lensMetadata.*  (camera original only)
  reason       provenance.reason                                       (rework edit exports only)
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


def clip_name(omc): return _fprops(omc).get("clipName")
def reel(omc): return _get(_fprops(omc), "cameraMetadata", "reelName")
def camera_serial(omc): return _get(_fprops(omc), "cameraMetadata", "cameraSerialNumber")


def _px(value) -> Optional[str]:
    return str(value).replace("px", "").strip() or None if value not in (None, "") else None


def width(omc): return _px(_get(omc, "AssetSC", "structuralProperties", "dimensions", "width"))
def height(omc): return _px(_get(omc, "AssetSC", "structuralProperties", "dimensions", "height"))
def color_space(omc): return _custom(omc).get("colorSpace")
def reason(omc): return _get(omc, "provenance", "reason")
def camera_make(omc): return _get(_fprops(omc), "cameraMetadata", "cameraMake")
def camera_model(omc): return _get(_fprops(omc), "cameraMetadata", "cameraModel")
def exposure_index(omc): return _get(_fprops(omc), "cameraMetadata", "exposureIndex")
def lens_make(omc): return _get(_fprops(omc), "lensMetadata", "lensMake")
def lens_model(omc): return _get(_fprops(omc), "lensMetadata", "lensModel")
def focal_length(omc): return _get(_fprops(omc), "lensMetadata", "focalLength")
def t_stop(omc): return _get(_fprops(omc), "lensMetadata", "tStop")


# ---- SQL equivalents (alias the versions table as `v`). Constants only: never interpolate user input. ----
_FP = "v.omc_json->'assetFC'->'functionalProperties'"
_CUSTOM = "v.omc_json->'AssetSC'->'customData'->0->'value'"  # the single poc/plc entry (the seed writes exactly one)

SQL_CODEC = "v.omc_json->'AssetSC'->'structuralProperties'->>'codec'"
SQL_CONTAINER = f"{_CUSTOM}->>'container'"
SQL_FPS = f"({_CUSTOM}->>'frameRate')::numeric(10,2)"
SQL_TIMECODE_IN = f"COALESCE({_FP}->'cameraMetadata'->>'timecodeStart', {_FP}->'timing'->>'sourceStart')"
SQL_TIMECODE_OUT = f"COALESCE({_FP}->'cameraMetadata'->>'timecodeEnd', {_FP}->'timing'->>'sourceEnd')"
SQL_CLIP_NAME = f"{_FP}->>'clipName'"
SQL_REEL = f"{_FP}->'cameraMetadata'->>'reelName'"
SQL_CAMERA_SERIAL = f"{_FP}->'cameraMetadata'->>'cameraSerialNumber'"
