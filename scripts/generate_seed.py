#!/usr/bin/env python3
"""Generate seed.sql per Appendix H specification."""
import json
from datetime import datetime, timedelta

def create_omc_json(base_shot_code, variant_code, human_readable_code, capture_time):
    """Create ARRI ALEXA Mini LF metadata JSON."""
    omc = {
        'camera_make': 'ARRI',
        'camera_model': 'ALEXA Mini LF',
        'serial_number': 'ALX-001234',
        'lens_model': 'ARRI Master Prime 35mm T1.3',
        'focal_length_mm': 35,
        'aperture': 2.8,
        'iso': 800,
        'frame_rate': 24.0,
        'resolution': '4448x3096',
        'codec': 'ARRIRAW',
        'color_space': 'ARRI Wide Gamut / LogC4',
        'timecode_start': '01:00:00:00',
        'timecode_end': '01:00:15:00',
        'capture_timestamp': capture_time,
        'base_shot_code': base_shot_code,
        'human_readable_code': human_readable_code
    }
    if variant_code:
        omc['variant_code'] = variant_code
    return json.dumps(omc).replace("'", "''")

# Shot definitions: (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description)
SHOTS = [
    ('011_001', '011_001', None, '011_001', '2026-01-15 08:00:00+00', 'Wide establishing shot'),
    ('011_001A', '011_001', 'A', '011_001A', '2026-01-15 08:15:00+00', 'Wide establishing shot - variant A'),
    ('011_001B', '011_001', 'B', '011_001B', '2026-01-15 08:30:00+00', 'Wide establishing shot - variant B'),
    ('011_002', '011_002', None, '011_002', '2026-01-15 09:00:00+00', 'Medium two-shot'),
    ('011_003', '011_003', None, '011_003', '2026-01-15 09:30:00+00', 'Close-up dialogue'),
    ('011_004', '011_004', None, '011_004', '2026-01-15 10:00:00+00', 'Over-shoulder'),
    ('012_001', '012_001', None, '012_001', '2026-01-15 11:00:00+00', 'Action sequence start'),
    ('012_002', '012_002', None, '012_002', '2026-01-15 11:30:00+00', 'Action sequence middle'),
    ('012_003', '012_003', None, '012_003', '2026-01-15 12:00:00+00', 'Action sequence end'),
    ('012_004', '012_004', None, '012_004', '2026-01-15 12:30:00+00', 'Reaction shot'),
    ('013_001', '013_001', None, '013_001', '2026-01-15 14:00:00+00', 'Interior wide'),
    ('013_002', '013_002', None, '013_002', '2026-01-15 14:30:00+00', 'Interior medium'),
    ('013_003', '013_003', None, '013_003', '2026-01-15 15:00:00+00', 'Interior close-up'),
    ('014_001', '014_001', None, '014_001', '2026-01-16 08:00:00+00', 'Exterior establishing'),
    ('014_002', '014_002', None, '014_002', '2026-01-16 08:30:00+00', 'Exterior medium'),
    ('014_003', '014_003', None, '014_003', '2026-01-16 09:00:00+00', 'Exterior close-up'),
    ('014_004', '014_004', None, '014_004', '2026-01-16 09:30:00+00', 'Exterior two-shot'),
    ('015_001', '015_001', None, '015_001', '2026-01-16 11:00:00+00', 'Dialogue scene A'),
    ('015_002', '015_002', None, '015_002', '2026-01-16 11:30:00+00', 'Dialogue scene B'),
    ('015_003', '015_003', None, '015_003', '2026-01-16 12:00:00+00', 'Dialogue scene C'),
    ('015_004', '015_004', None, '015_004', '2026-01-16 12:30:00+00', 'Dialogue scene D'),
    ('015_005', '015_005', None, '015_005', '2026-01-16 13:00:00+00', 'Dialogue scene E'),
    ('016_001', '016_001', None, '016_001', '2026-01-16 14:00:00+00', 'Transition shot'),
    ('017_001', '017_001', None, '017_001', '2026-01-17 08:00:00+00', 'Climax sequence A'),
    ('017_002', '017_002', None, '017_002', '2026-01-17 08:30:00+00', 'Climax sequence B'),
    ('017_003', '017_003', None, '017_003', '2026-01-17 09:00:00+00', 'Climax sequence C'),
    ('017_004', '017_004', None, '017_004', '2026-01-17 09:30:00+00', 'Climax sequence D'),
    ('018_001', '018_001', None, '018_001', '2026-01-17 11:00:00+00', 'Resolution scene A'),
    ('018_002', '018_002', None, '018_002', '2026-01-17 11:30:00+00', 'Resolution scene B'),
    ('018_003', '018_003', None, '018_003', '2026-01-17 12:00:00+00', 'Resolution scene C'),
    ('019_001', '019_001', None, '019_001', '2026-01-17 14:00:00+00', 'Final shot'),
    ('019_002', '019_002', None, '019_002', '2026-01-17 14:30:00+00', 'Final shot variant'),
]

# Rework cases: (shot_idx, rework_type, reason)
# 2 editorial, 1 VFX, 1 creative
REWORK_CASES = [
    (0, 'editorial', 'Editorial re-cut for pacing'),  # 011_001
    (5, 'editorial', 'Editorial re-cut for continuity'),  # 011_004
    (6, 'vfx', 'VFX revision requested'),  # 012_001
    (13, 'creative', 'Director notes - creative rework'),  # 014_001
]

def format_uuid(base, idx):
    """Format UUID with proper hex."""
    hex_str = f'{base + idx:04x}'.lower()
    return f'550e8400-e29b-41d4-a716-44665544{hex_str}'

def main():
    output = []
    output.append("-- Production Lineage Concierge POC - Seed Data")
    output.append("-- Regenerated per Appendix H (Seed Data Specification)")
    output.append("-- Single episodic production, 3 shoot days, 28 shots total")
    output.append("-- ARRI ALEXA Mini LF metadata, lettered variants, 4 rework cases")
    output.append("")
    output.append("-- Clear existing demo data")
    output.append("TRUNCATE TABLE events, package_members, packages, version_lineage, versions, assets, shots, productions CASCADE;")
    output.append("")

    # Production
    output.append("-- Production")
    output.append("INSERT INTO productions (id, code, title, created_at)")
    output.append("VALUES ('550e8400-e29b-41d4-a716-446655440000', 'EXFTR', 'Example Feature (Demo)', '2026-01-15 08:00:00+00'::timestamptz)")
    output.append("ON CONFLICT (code) DO UPDATE SET title = EXCLUDED.title;")
    output.append("")

    # Shots
    output.append("-- Shots: 28 shots across 3 shoot days")
    output.append("INSERT INTO shots (id, production_id, shot_code, scene, description, created_at)")
    output.append("VALUES")
    shot_values = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        shot_id = format_uuid(0x001, idx)
        scene = shot_code.split('_')[0]
        shot_values.append(f"    ('{shot_id}', '550e8400-e29b-41d4-a716-446655440000', '{shot_code}', '{scene}', '{description}', '{capture_time}'::timestamptz)")
    output.append(',\n'.join(shot_values))
    output.append("ON CONFLICT (production_id, shot_code) DO NOTHING;")
    output.append("")

    # Assets
    output.append("-- Assets: One asset per shot (28 total)")
    output.append("INSERT INTO assets (id, shot_id, production_id, asset_type, clip_name, reel_or_roll, camera_serial, created_at)")
    output.append("VALUES")
    asset_values = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        asset_id = format_uuid(0x101, idx)
        shot_id = format_uuid(0x001, idx)
        reel = f"A{idx // 10 + 1:03d}"
        clip_name = f"{reel}C{idx % 10 + 1:03d}_{shot_code}.mxf"
        asset_values.append(f"    ('{asset_id}', '{shot_id}', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', '{clip_name}', '{reel}', 'ALX-001234', '{capture_time}'::timestamptz)")
    output.append(',\n'.join(asset_values))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Versions: CAMERA_ORIGINAL
    output.append("-- Versions: CAMERA_ORIGINAL (28 total)")
    output.append("INSERT INTO versions (id, asset_id, version_type, storage_uri, codec, container, fps, timecode_in, timecode_out, omc_json, created_at)")
    output.append("VALUES")
    cam_values = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        version_id = format_uuid(0x201, idx)
        asset_id = format_uuid(0x101, idx)
        omc_json = create_omc_json(base_shot_code, variant_code, human_readable_code, capture_time)
        cam_values.append(f"    ('{version_id}', '{asset_id}', 'CAMERA_ORIGINAL', 'dam://camera_originals/{shot_code}.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{omc_json}'::jsonb, '{capture_time}'::timestamptz)")
    output.append(',\n'.join(cam_values))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Versions: HDE_MASTER (derived from camera originals, created hours later)
    output.append("-- Versions: HDE_MASTER (28 total, derived from camera originals)")
    output.append("INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)")
    output.append("VALUES")
    hde_values = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        version_id = format_uuid(0x301, idx)
        asset_id = format_uuid(0x101, idx)
        cam_version_id = format_uuid(0x201, idx)
        # HDE created 2-4 hours after capture
        hde_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(hours=2 + (idx % 3))).isoformat().replace('+00:00', '+00')
        hde_values.append(f"    ('{version_id}', '{asset_id}', 'HDE_MASTER', '{cam_version_id}', 'dam://hde_masters/{shot_code}.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '{hde_time}'::timestamptz)")
    output.append(',\n'.join(hde_values))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Versions: DAILIES_PROXY (derived from HDE masters, created same day or overnight)
    output.append("-- Versions: DAILIES_PROXY (28 total, derived from HDE masters)")
    output.append("INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)")
    output.append("VALUES")
    dailies_values = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        version_id = format_uuid(0x401, idx)
        asset_id = format_uuid(0x101, idx)
        hde_version_id = format_uuid(0x301, idx)
        # Dailies created 6-12 hours after capture (overnight)
        dailies_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(hours=8 + (idx % 5))).isoformat().replace('+00:00', '+00')
        dailies_values.append(f"    ('{version_id}', '{asset_id}', 'DAILIES_PROXY', '{hde_version_id}', 'dam://dailies/{shot_code}.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', '{dailies_time}'::timestamptz)")
    output.append(',\n'.join(dailies_values))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Versions: EDIT_EXPORT (most shots, but not all - some blocked)
    # Skip last 4 shots to create blocked cases
    output.append("-- Versions: EDIT_EXPORT (24 total, 4 shots blocked)")
    output.append("INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)")
    output.append("VALUES")
    edit_values = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        if idx >= 24:  # Last 4 shots don't have edit exports (blocked)
            continue
        version_id = format_uuid(0x501, idx)
        asset_id = format_uuid(0x101, idx)
        dailies_version_id = format_uuid(0x401, idx)
        # Edit exports created 2-5 days after capture
        edit_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(days=2 + (idx % 4))).isoformat().replace('+00:00', '+00')
        edit_values.append(f"    ('{version_id}', '{asset_id}', 'EDIT_EXPORT', '{dailies_version_id}', 'dam://edit_exports/{shot_code}.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '{edit_time}'::timestamptz)")
    output.append(',\n'.join(edit_values))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Rework versions: EDIT_EXPORT (for rework cases)
    # 2 editorial re-cuts, 1 VFX revision, 1 creative rework
    output.append("-- Versions: Rework EDIT_EXPORT (4 rework cases)")
    output.append("INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, creative_context, created_at)")
    output.append("VALUES")
    rework_values = []
    rework_idx = 0
    for shot_idx, rework_type, reason in REWORK_CASES:
        shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description = SHOTS[shot_idx]
        version_id = format_uuid(0x601, rework_idx)
        asset_id = format_uuid(0x101, shot_idx)
        # Rework derives from original edit export
        original_edit_id = format_uuid(0x501, shot_idx)
        rework_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(days=5 + rework_idx)).isoformat().replace('+00:00', '+00')
        creative_context = json.dumps({'rework_type': rework_type, 'reason': reason}).replace("'", "''")
        rework_values.append(f"    ('{version_id}', '{asset_id}', 'EDIT_EXPORT', '{original_edit_id}', 'dam://edit_exports/{shot_code}_v2.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '{creative_context}'::jsonb, '{rework_time}'::timestamptz)")
        rework_idx += 1
    output.append(',\n'.join(rework_values))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Version Lineage edges
    output.append("-- Version Lineage: Explicit edges for all derivations")
    output.append("INSERT INTO version_lineage (derived_version_id, source_version_id, transform_type, created_at)")
    output.append("VALUES")
    lineage_values = []
    for idx in range(len(SHOTS)):
        # CAMERA_ORIGINAL -> HDE_MASTER
        cam_id = format_uuid(0x201, idx)
        hde_id = format_uuid(0x301, idx)
        hde_time = (datetime.fromisoformat(SHOTS[idx][4].replace('+00', '+00:00')) + timedelta(hours=2 + (idx % 3))).isoformat().replace('+00:00', '+00')
        lineage_values.append(f"    ('{hde_id}', '{cam_id}', 'HDE_TRANSCODE', '{hde_time}'::timestamptz)")

        # HDE_MASTER -> DAILIES_PROXY
        dailies_id = format_uuid(0x401, idx)
        dailies_time = (datetime.fromisoformat(SHOTS[idx][4].replace('+00', '+00:00')) + timedelta(hours=8 + (idx % 5))).isoformat().replace('+00:00', '+00')
        lineage_values.append(f"    ('{dailies_id}', '{hde_id}', 'DAILIES_ENCODE', '{dailies_time}'::timestamptz)")

        # DAILIES_PROXY -> EDIT_EXPORT (for shots with edit exports)
        if idx < 24:
            edit_id = format_uuid(0x501, idx)
            edit_time = (datetime.fromisoformat(SHOTS[idx][4].replace('+00', '+00:00')) + timedelta(days=2 + (idx % 4))).isoformat().replace('+00:00', '+00')
            lineage_values.append(f"    ('{edit_id}', '{dailies_id}', 'EDIT_EXPORT', '{edit_time}'::timestamptz)")

        # EDIT_EXPORT -> Rework EDIT_EXPORT (for rework cases)
        for rework_idx, (shot_idx, rework_type, reason) in enumerate(REWORK_CASES):
            if shot_idx == idx:
                rework_id = format_uuid(0x601, rework_idx)
                original_edit_id = format_uuid(0x501, idx)
                rework_time = (datetime.fromisoformat(SHOTS[idx][4].replace('+00', '+00:00')) + timedelta(days=5 + rework_idx)).isoformat().replace('+00:00', '+00')
                lineage_values.append(f"    ('{rework_id}', '{original_edit_id}', 'REWORK_{rework_type.upper()}', '{rework_time}'::timestamptz)")
    output.append(',\n'.join(lineage_values))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Events: CAPTURE
    output.append("-- Events: CAPTURE (28 total)")
    output.append("INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)")
    output.append("VALUES")
    capture_events = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        shot_id = format_uuid(0x001, idx)
        cam_version_id = format_uuid(0x201, idx)
        capture_events.append(f"    ('{shot_id}', 'CAPTURE', '{cam_version_id}', 'Camera Operator', 'ARRI ALEXA Mini LF', '{capture_time}'::timestamptz)")
    output.append(',\n'.join(capture_events))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Events: HDE_TRANSCODE
    output.append("-- Events: HDE_TRANSCODE (28 total)")
    output.append("INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)")
    output.append("VALUES")
    hde_events = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        shot_id = format_uuid(0x001, idx)
        hde_version_id = format_uuid(0x301, idx)
        hde_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(hours=2 + (idx % 3))).isoformat().replace('+00:00', '+00')
        hde_events.append(f"    ('{shot_id}', 'HDE_TRANSCODE', '{hde_version_id}', 'DIT', 'Offload Service', '{hde_time}'::timestamptz)")
    output.append(',\n'.join(hde_events))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Events: DAILIES_PUBLISHED
    output.append("-- Events: DAILIES_PUBLISHED (28 total)")
    output.append("INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)")
    output.append("VALUES")
    dailies_events = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        shot_id = format_uuid(0x001, idx)
        dailies_version_id = format_uuid(0x401, idx)
        dailies_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(hours=8 + (idx % 5))).isoformat().replace('+00:00', '+00')
        dailies_events.append(f"    ('{shot_id}', 'DAILIES_PUBLISHED', '{dailies_version_id}', 'Dailies Operator', 'Dailies Service', '{dailies_time}'::timestamptz)")
    output.append(',\n'.join(dailies_events))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Events: EDIT_EXPORT_CREATED (for shots with edit exports)
    output.append("-- Events: EDIT_EXPORT_CREATED (24 total, 4 shots blocked)")
    output.append("INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)")
    output.append("VALUES")
    edit_events = []
    for idx, (shot_code, base_shot_code, variant_code, human_readable_code, capture_time, description) in enumerate(SHOTS):
        if idx >= 24:
            continue
        shot_id = format_uuid(0x001, idx)
        edit_version_id = format_uuid(0x501, idx)
        edit_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(days=2 + (idx % 4))).isoformat().replace('+00:00', '+00')
        edit_events.append(f"    ('{shot_id}', 'EDIT_EXPORT_CREATED', '{edit_version_id}', 'Editor', 'Avid Media Composer', '{edit_time}'::timestamptz)")
    output.append(',\n'.join(edit_events))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Events: Rework EDIT_EXPORT_CREATED (for rework cases)
    output.append("-- Events: Rework EDIT_EXPORT_CREATED (4 rework cases)")
    output.append("INSERT INTO events (shot_id, event_type, version_id, actor, tool, details, created_at)")
    output.append("VALUES")
    rework_events = []
    for rework_idx, (shot_idx, rework_type, reason) in enumerate(REWORK_CASES):
        shot_id = format_uuid(0x001, shot_idx)
        rework_version_id = format_uuid(0x601, rework_idx)
        capture_time = SHOTS[shot_idx][4]
        rework_time = (datetime.fromisoformat(capture_time.replace('+00', '+00:00')) + timedelta(days=5 + rework_idx)).isoformat().replace('+00:00', '+00')
        details = json.dumps({'rework_type': rework_type, 'reason': reason}).replace("'", "''")
        rework_events.append(f"    ('{shot_id}', 'EDIT_EXPORT_CREATED', '{rework_version_id}', 'Editor', 'Avid Media Composer', '{details}'::jsonb, '{rework_time}'::timestamptz)")
    output.append(',\n'.join(rework_events))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Packages: TURNOVER (package with some edit exports)
    output.append("-- Packages: TURNOVER")
    output.append("INSERT INTO packages (id, production_id, package_type, label, vendor, created_at)")
    output.append("VALUES")
    turnover_pkg_id = '550e8400-e29b-41d4-a716-446655440701'
    turnover_time = (datetime.fromisoformat('2026-01-17 10:00:00+00:00') + timedelta(days=3)).isoformat().replace('+00:00', '+00')
    output.append(f"    ('{turnover_pkg_id}', '550e8400-e29b-41d4-a716-446655440000', 'TURNOVER', 'VFX Turnover - Scenes 011-015', 'VFX Vendor Alpha', '{turnover_time}'::timestamptz)")
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Package Members: TURNOVER (include some edit exports)
    output.append("-- Package Members: TURNOVER (12 shots)")
    output.append("INSERT INTO package_members (package_id, version_id, created_at)")
    output.append("VALUES")
    turnover_members = []
    for idx in range(12):  # First 12 shots with edit exports
        if idx >= 24:
            continue
        edit_version_id = format_uuid(0x501, idx)
        turnover_members.append(f"    ('{turnover_pkg_id}', '{edit_version_id}', '{turnover_time}'::timestamptz)")
    output.append(',\n'.join(turnover_members))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Events: TURNOVER_DELIVERED
    output.append("-- Events: TURNOVER_DELIVERED")
    output.append("INSERT INTO events (shot_id, event_type, package_id, actor, tool, created_at)")
    output.append("VALUES")
    turnover_delivered = []
    for idx in range(12):
        if idx >= 24:
            continue
        shot_id = format_uuid(0x001, idx)
        turnover_delivered.append(f"    ('{shot_id}', 'TURNOVER_DELIVERED', '{turnover_pkg_id}', 'Post Supervisor', 'Package Service', '{turnover_time}'::timestamptz)")
    output.append(',\n'.join(turnover_delivered))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Packages: ARCHIVE
    output.append("-- Packages: ARCHIVE")
    output.append("INSERT INTO packages (id, production_id, package_type, label, vendor, created_at)")
    output.append("VALUES")
    archive_pkg_id = '550e8400-e29b-41d4-a716-446655440702'
    archive_time = (datetime.fromisoformat('2026-01-20 10:00:00+00:00')).isoformat().replace('+00:00', '+00')
    output.append(f"    ('{archive_pkg_id}', '550e8400-e29b-41d4-a716-446655440000', 'ARCHIVE', 'Archive Package - Initial Deliverables', NULL, '{archive_time}'::timestamptz)")
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Package Members: ARCHIVE (using HDE_MASTER as highest quality source)
    output.append("-- Package Members: ARCHIVE (8 shots)")
    output.append("INSERT INTO package_members (package_id, version_id, created_at)")
    output.append("VALUES")
    archive_members = []
    for idx in range(8):  # First 8 shots
        hde_version_id = format_uuid(0x301, idx)
        archive_members.append(f"    ('{archive_pkg_id}', '{hde_version_id}', '{archive_time}'::timestamptz)")
    output.append(',\n'.join(archive_members))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    # Events: ARCHIVED
    output.append("-- Events: ARCHIVED")
    output.append("INSERT INTO events (shot_id, event_type, package_id, actor, tool, created_at)")
    output.append("VALUES")
    archived_events = []
    for idx in range(8):
        shot_id = format_uuid(0x001, idx)
        archived_events.append(f"    ('{shot_id}', 'ARCHIVED', '{archive_pkg_id}', 'Archive Operator', 'Archive Service', '{archive_time}'::timestamptz)")
    output.append(',\n'.join(archived_events))
    output.append("ON CONFLICT DO NOTHING;")
    output.append("")

    print('\n'.join(output))

if __name__ == '__main__':
    main()
