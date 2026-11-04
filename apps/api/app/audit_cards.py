"""Extra fields for the Ask page's version audit cards.

The Ask templates select a base column set per version (see VERSION_CARD_COLUMNS in ask_templates.py). Each card type
(camera original, derived media, edit export) shows more than that, so every version row is enriched here with the
whole superset. A key is always present and is None / [] when the version type cannot carry it; the card decides
what to show per type, so the data shape never depends on the layout.

Sources (single-source rule from Phase B: values come from omc_json via omc_fields.py, or from events / packages):
  format / timecode / camera / lens / reason   the version's own omc_json
  source_reel / source_clip_name               omc_json of the ROOT camera original, found by walking
                                               derived_from_version_id upwards (derived media only)
  created_by_actor / created_by_tool           the event that created the version (events.version_id)
  delivered_in                                 package_members -> packages
"""
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import omc_fields as f

_IDS = "CAST(:ids AS uuid[])"


def enrich_version_cards(db: Session, versions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add the card fields to each version dict (in place) and return the list."""
    if not versions:
        return versions
    ids = [str(v["id"]) for v in versions]

    omc = {str(r[0]): r[1] for r in db.execute(
        text(f"SELECT id, omc_json FROM versions WHERE id = ANY({_IDS})"), {"ids": ids})}

    roots = {str(r[0]): r[1] for r in db.execute(text(f"""
        WITH RECURSIVE up AS (
            SELECT v.id AS start_id, v.id, v.derived_from_version_id, v.version_type, v.omc_json, 0 AS depth
            FROM versions v WHERE v.id = ANY({_IDS})
            UNION ALL
            SELECT up.start_id, p.id, p.derived_from_version_id, p.version_type, p.omc_json, up.depth + 1
            FROM versions p JOIN up ON p.id = up.derived_from_version_id
            WHERE up.depth < 20
        )
        SELECT start_id, omc_json FROM up WHERE version_type = 'CAMERA_ORIGINAL'
    """), {"ids": ids})}

    created_by = {str(r[0]): (r[1], r[2]) for r in db.execute(text(f"""
        SELECT version_id, actor, tool FROM events
        WHERE version_id = ANY({_IDS})
          AND event_type IN ('CAPTURE', 'DEBAYER_TRANSCODE', 'DAILIES_PUBLISHED', 'EDIT_EXPORT_CREATED')
    """), {"ids": ids})}

    delivered: Dict[str, List[Dict[str, Any]]] = {}
    for vid, ptype, label, vendor in db.execute(text(f"""
        SELECT pm.version_id, pk.package_type, pk.label, pk.vendor
        FROM package_members pm JOIN packages pk ON pk.id = pm.package_id
        WHERE pm.version_id = ANY({_IDS})
        ORDER BY pk.package_type DESC, pk.label
    """), {"ids": ids}):
        delivered.setdefault(str(vid), []).append({"package_type": ptype, "label": label, "vendor": vendor})

    for v in versions:
        vid = str(v["id"])
        j = omc.get(vid)
        is_camera = v.get("version_type") == "CAMERA_ORIGINAL"
        root = None if is_camera else roots.get(vid)
        actor, tool = created_by.get(vid, (None, None))
        v.update({
            "container": f.container(j),
            "width": f.width(j),
            "height": f.height(j),
            "color_space": f.color_space(j),
            "clip_name": f.clip_name(j),
            "camera_make": f.camera_make(j),
            "camera_model": f.camera_model(j),
            "camera_serial": f.camera_serial(j),
            "exposure_index": f.exposure_index(j),
            "lens_make": f.lens_make(j),
            "lens_model": f.lens_model(j),
            "focal_length": f.focal_length(j),
            "t_stop": f.t_stop(j),
            "source_reel": f.reel(root) if root else None,
            "source_clip_name": f.clip_name(root) if root else None,
            "reason": f.reason(j),
            "created_by_actor": actor,
            "created_by_tool": tool,
            "delivered_in": delivered.get(vid, []),
        })
    return versions
