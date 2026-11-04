"""Deterministic Ask template implementations."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
from uuid import UUID

from app.omc_fields import (
    SQL_CODEC, SQL_FPS, SQL_TIMECODE_IN, SQL_TIMECODE_OUT, SQL_CLIP_NAME, SQL_REEL,
)

# Every template that returns `evidence.versions` selects at least these columns (alias the table as `v`). They are
# exactly what the Ask page's VersionAuditCard displays, so a card can never show "—" for something the data holds.
# `reel` is camera metadata: it is NULL for every stage after CAMERA_ORIGINAL by design (see omc_fields.py).
# Keep `id` first: the card takes the first UUID-valued key as the Version ID.
VERSION_CARD_COLUMNS = f"""v.id, v.version_type, v.storage_uri, v.created_at,
               {SQL_CODEC} AS codec, {SQL_FPS} AS fps,
               {SQL_TIMECODE_IN} AS timecode_in, {SQL_TIMECODE_OUT} AS timecode_out,
               {SQL_REEL} AS reel"""


def latest_camera_original(db: Session, shot_code: str, production_code: str) -> Dict[str, Any]:
    """Template: latest_camera_original(shot_code)"""
    query = text(f"""
        SELECT {VERSION_CARD_COLUMNS}
        FROM versions v
        JOIN assets a ON v.asset_id = a.id
        JOIN shots s ON a.shot_id = s.id
        JOIN productions p ON s.production_id = p.id
        WHERE s.shot_code = :shot_code
          AND p.code = :production_code
          AND v.version_type = 'CAMERA_ORIGINAL'
        ORDER BY v.created_at DESC
        LIMIT 1
    """)
    result = db.execute(query, {"shot_code": shot_code, "production_code": production_code})
    row = result.fetchone()

    if not row:
        return {
            "template": "latest_camera_original",
            "params": {"shot_code": shot_code},
            "answer": f"No camera original found for shot {shot_code}",
            "evidence": {"versions": []},
            "explanation": f"Query for latest CAMERA_ORIGINAL version of shot {shot_code}"
        }

    version = dict(row._mapping)
    return {
        "template": "latest_camera_original",
        "params": {"shot_code": shot_code},
        "answer": f"Latest camera original for {shot_code}: {version['storage_uri']}",
        "evidence": {"versions": [version]},
        "explanation": f"Query for latest CAMERA_ORIGINAL version of shot {shot_code}"
    }


def lineage_chain_to_latest_edit_export(db: Session, shot_code: str, production_code: str) -> Dict[str, Any]:
    """Template: lineage_chain_to_latest_edit_export(shot_code)"""
    # Get all versions for this shot, ordered by lineage
    # Returns chain ordered root-first (depth DESC): CAMERA_ORIGINAL → ... → EDIT_EXPORT
    # The recursion only walks ids; the final SELECT joins back to versions for the card columns.
    query = text(f"""
        WITH RECURSIVE lineage_chain AS (
            -- Anchor: Start with latest EDIT_EXPORT (wrapped in subquery to allow ORDER BY/LIMIT)
            SELECT v.id, v.version_type, v.derived_from_version_id, v.storage_uri, v.created_at, 0 as depth
            FROM (
                SELECT v.id, v.version_type, v.derived_from_version_id, v.storage_uri, v.created_at
                FROM versions v
                JOIN assets a ON v.asset_id = a.id
                JOIN shots s ON a.shot_id = s.id
                JOIN productions p ON s.production_id = p.id
                WHERE s.shot_code = :shot_code
                  AND p.code = :production_code
                  AND v.version_type = 'EDIT_EXPORT'
                ORDER BY v.created_at DESC, v.id DESC
                LIMIT 1
            ) v

            UNION ALL

            -- Recursive member: Follow derived_from_version_id backwards with cycle protection
            SELECT v.id, v.version_type, v.derived_from_version_id, v.storage_uri, v.created_at, lc.depth + 1
            FROM versions v
            JOIN lineage_chain lc ON v.id = lc.derived_from_version_id
            WHERE lc.depth < 20
        )
        SELECT {VERSION_CARD_COLUMNS}, lc.derived_from_version_id
        FROM lineage_chain lc
        JOIN versions v ON v.id = lc.id
        ORDER BY lc.depth DESC
    """)
    result = db.execute(query, {"shot_code": shot_code, "production_code": production_code})
    rows = result.fetchall()

    chain = [dict(row._mapping) for row in rows]

    if not chain:
        return {
            "template": "lineage_chain_to_latest_edit_export",
            "params": {"shot_code": shot_code},
            "answer": f"No edit export found for shot {shot_code}",
            "evidence": {"versions": []},
            "explanation": f"Query for lineage chain from camera original to latest EDIT_EXPORT for shot {shot_code}"
        }

    chain_types = " → ".join([v["version_type"] for v in chain])
    return {
        "template": "lineage_chain_to_latest_edit_export",
        "params": {"shot_code": shot_code},
        "answer": f"Lineage chain for {shot_code}: {chain_types}",
        "evidence": {"versions": chain},
        "explanation": f"Query for lineage chain from camera original to latest EDIT_EXPORT for shot {shot_code}"
    }


def shots_with_dailies_no_edit_export(db: Session, production_code: str) -> Dict[str, Any]:
    """Template: shots_with_dailies_no_edit_export()"""
    query = text("""
        SELECT DISTINCT s.shot_code, s.scene, s.description, vs.stage
        FROM shots s
        JOIN productions p ON s.production_id = p.id
        LEFT JOIN v_shot_stage vs ON s.id = vs.shot_id
        WHERE p.code = :production_code
          AND EXISTS (
              SELECT 1 FROM events e
              WHERE e.shot_id = s.id AND e.event_type = 'DAILIES_PUBLISHED'
          )
          AND NOT EXISTS (
              SELECT 1 FROM events e
              WHERE e.shot_id = s.id AND e.event_type = 'EDIT_EXPORT_CREATED'
          )
    """)
    result = db.execute(query, {"production_code": production_code})
    rows = result.fetchall()

    shots = [dict(row._mapping) for row in rows]

    return {
        "template": "shots_with_dailies_no_edit_export",
        "params": {},
        "answer": f"Found {len(shots)} shot(s) with dailies but no edit export",
        "evidence": {"shots": shots},
        "explanation": "Query for shots that have DAILIES_PUBLISHED events but no EDIT_EXPORT_CREATED events"
    }


def shots_ready_for_turnover_and_missing(db: Session, production_code: str) -> Dict[str, Any]:
    """Template: shots_ready_for_turnover_and_missing()"""
    query = text("""
        SELECT DISTINCT s.shot_code, s.scene, s.description, vs.stage
        FROM shots s
        JOIN productions p ON s.production_id = p.id
        LEFT JOIN v_shot_stage vs ON s.id = vs.shot_id
        WHERE p.code = :production_code
          AND EXISTS (
              SELECT 1 FROM events e
              WHERE e.shot_id = s.id AND e.event_type = 'EDIT_EXPORT_CREATED'
          )
          AND NOT EXISTS (
              SELECT 1 FROM events e
              WHERE e.shot_id = s.id AND e.event_type = 'TURNOVER_DELIVERED'
          )
    """)
    result = db.execute(query, {"production_code": production_code})
    rows = result.fetchall()

    shots = [dict(row._mapping) for row in rows]

    return {
        "template": "shots_ready_for_turnover_and_missing",
        "params": {},
        "answer": f"Found {len(shots)} shot(s) ready for turnover but not yet delivered",
        "evidence": {"shots": shots},
        "explanation": "Query for shots with EDIT_EXPORT_CREATED but no TURNOVER_DELIVERED"
    }


def package_members(db: Session, package_id: str, production_code: str) -> Dict[str, Any]:
    """Template: package_members(package_id)

    `production_code` is injected by every Ask route; the package must belong to that production.
    """
    query = text(f"""
        SELECT {VERSION_CARD_COLUMNS}
        FROM versions v
        JOIN package_members pm ON v.id = pm.version_id
        JOIN packages pk ON pk.id = pm.package_id
        JOIN productions p ON p.id = pk.production_id
        WHERE pm.package_id = CAST(:package_id AS uuid)
          AND p.code = :production_code
        ORDER BY v.created_at
    """)
    result = db.execute(query, {"package_id": package_id, "production_code": production_code})
    rows = result.fetchall()

    versions = [dict(row._mapping) for row in rows]

    return {
        "template": "package_members",
        "params": {"package_id": package_id},
        "answer": f"Package {package_id} contains {len(versions)} version(s)",
        "evidence": {"versions": versions},
        "explanation": f"Query for all versions in package {package_id}"
    }


def source_relink_keys(db: Session, shot_code: str, production_code: str) -> Dict[str, Any]:
    """Template: source_relink_keys(shot_code)"""
    query = text(f"""
        SELECT {VERSION_CARD_COLUMNS}, {SQL_CLIP_NAME} AS clip_name
        FROM versions v
        JOIN assets a ON v.asset_id = a.id
        JOIN shots s ON a.shot_id = s.id
        JOIN productions p ON s.production_id = p.id
        WHERE s.shot_code = :shot_code
          AND p.code = :production_code
          AND v.version_type = 'CAMERA_ORIGINAL'
        ORDER BY v.created_at DESC
        LIMIT 1
    """)
    result = db.execute(query, {"shot_code": shot_code, "production_code": production_code})
    row = result.fetchone()

    if not row:
        return {
            "template": "source_relink_keys",
            "params": {"shot_code": shot_code},
            "answer": f"No camera original found for shot {shot_code}",
            "evidence": {"versions": []},
            "explanation": f"Query for relink keys (fps, timecode) for camera original of shot {shot_code}"
        }

    version = dict(row._mapping)
    return {
        "template": "source_relink_keys",
        "params": {"shot_code": shot_code},
        "answer": f"Relink keys for {shot_code}: fps={version['fps']}, tc_in={version['timecode_in']}, tc_out={version['timecode_out']}",
        "evidence": {"versions": [version]},
        "explanation": f"Query for relink keys (fps, timecode) for camera original of shot {shot_code}"
    }


def latest_versions_by_type(db: Session, shot_code: str, production_code: str) -> Dict[str, Any]:
    """Template: latest_versions_by_type(shot_code)"""
    query = text(f"""
        SELECT DISTINCT ON (v.version_type)
            {VERSION_CARD_COLUMNS}
        FROM versions v
        JOIN assets a ON v.asset_id = a.id
        JOIN shots s ON a.shot_id = s.id
        JOIN productions p ON s.production_id = p.id
        WHERE s.shot_code = :shot_code
          AND p.code = :production_code
        ORDER BY v.version_type, v.created_at DESC
    """)
    result = db.execute(query, {"shot_code": shot_code, "production_code": production_code})
    rows = result.fetchall()

    versions = [dict(row._mapping) for row in rows]

    return {
        "template": "latest_versions_by_type",
        "params": {"shot_code": shot_code},
        "answer": f"Found {len(versions)} version type(s) for shot {shot_code}",
        "evidence": {"versions": versions},
        "explanation": f"Query for latest version of each type for shot {shot_code}"
    }


def archive_status(db: Session, production_code: str) -> Dict[str, Any]:
    """Template: archive_status(production_code)"""
    query = text("""
        SELECT
            COUNT(DISTINCT CASE WHEN e.id IS NOT NULL THEN s.id END) as archived_count,
            COUNT(DISTINCT s.id) as total_shots
        FROM shots s
        JOIN productions p ON s.production_id = p.id
        LEFT JOIN events e ON s.id = e.shot_id AND e.event_type = 'ARCHIVED'
        WHERE p.code = :production_code
    """)
    result = db.execute(query, {"production_code": production_code})
    row = result.fetchone()

    if row:
        archived = row[0] if row[0] is not None else 0
        total = row[1] if row[1] is not None else 0
        return {
            "template": "archive_status",
            "params": {"production_code": production_code},
            "answer": f"Archive status: {archived} of {total} shots archived",
            "evidence": {"summary": [{"archived": archived, "total": total}]},
            "explanation": f"Query for archive completion status for production {production_code}"
        }

    return {
        "template": "archive_status",
        "params": {"production_code": production_code},
        "answer": f"No shots found for production {production_code}",
        "evidence": {"summary": []},
        "explanation": f"Query for archive completion status for production {production_code}"
    }


# Template registry
TEMPLATES = {
    "latest_camera_original": latest_camera_original,
    "lineage_chain_to_latest_edit_export": lineage_chain_to_latest_edit_export,
    "shots_with_dailies_no_edit_export": shots_with_dailies_no_edit_export,
    "shots_ready_for_turnover_and_missing": shots_ready_for_turnover_and_missing,
    "package_members": package_members,
    "source_relink_keys": source_relink_keys,
    "latest_versions_by_type": latest_versions_by_type,
    "archive_status": archive_status,
}


def route_question(question: str) -> tuple[str, Dict[str, Any]]:
    """Simple keyword-based routing to templates."""
    question_lower = question.lower()

    if "camera original" in question_lower or "latest source" in question_lower:
        # Extract shot_code if present
        import re
        shot_match = re.search(r'shot\s+(\d+_\d+)', question_lower)
        if shot_match:
            return "latest_camera_original", {"shot_code": shot_match.group(1)}

    if "lineage" in question_lower or "chain" in question_lower:
        import re
        shot_match = re.search(r'shot\s+(\d+_\d+)', question_lower)
        if shot_match:
            return "lineage_chain_to_latest_edit_export", {"shot_code": shot_match.group(1)}

    if "dailies" in question_lower and "no edit" in question_lower:
        return "shots_with_dailies_no_edit_export", {}

    if "turnover" in question_lower and ("missing" in question_lower or "ready" in question_lower):
        return "shots_ready_for_turnover_and_missing", {}

    if "package" in question_lower and "member" in question_lower:
        import re
        uuid_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', question_lower)
        if uuid_match:
            return "package_members", {"package_id": uuid_match.group(1)}

    if "relink" in question_lower:
        import re
        shot_match = re.search(r'shot\s+(\d+_\d+)', question_lower)
        if shot_match:
            return "source_relink_keys", {"shot_code": shot_match.group(1)}

    if "latest version" in question_lower or "versions by type" in question_lower:
        import re
        shot_match = re.search(r'shot\s+(\d+_\d+)', question_lower)
        if shot_match:
            return "latest_versions_by_type", {"shot_code": shot_match.group(1)}

    if "archive" in question_lower and "status" in question_lower:
        return "archive_status", {}

    return None, {}
