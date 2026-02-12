-- Production Lineage Concierge POC - Seed Data
-- Regenerated per Appendix H (Seed Data Specification)
-- Single episodic production, 3 shoot days, 28 shots total
-- ARRI ALEXA Mini LF metadata, lettered variants, 4 rework cases

-- Clear existing demo data
TRUNCATE TABLE events, package_members, packages, version_lineage, versions, assets, shots, productions CASCADE;

-- Production
INSERT INTO productions (id, code, title, created_at)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'EXFTR', 'Example Feature (Demo)', '2026-01-15 08:00:00+00'::timestamptz)
ON CONFLICT (code) DO UPDATE SET title = EXCLUDED.title;

-- Shots: 28 shots across 3 shoot days
INSERT INTO shots (id, production_id, shot_code, scene, description, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', '011_001', '011', 'Wide establishing shot', '2026-01-15 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', '011_001A', '011', 'Wide establishing shot - variant A', '2026-01-15 08:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', '011_001B', '011', 'Wide establishing shot - variant B', '2026-01-15 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440000', '011_002', '011', 'Medium two-shot', '2026-01-15 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440000', '011_003', '011', 'Close-up dialogue', '2026-01-15 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440000', '011_004', '011', 'Over-shoulder', '2026-01-15 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440000', '012_001', '012', 'Action sequence start', '2026-01-15 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440000', '012_002', '012', 'Action sequence middle', '2026-01-15 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440000', '012_003', '012', 'Action sequence end', '2026-01-15 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000a', '550e8400-e29b-41d4-a716-446655440000', '012_004', '012', 'Reaction shot', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000b', '550e8400-e29b-41d4-a716-446655440000', '013_001', '013', 'Interior wide', '2026-01-15 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000c', '550e8400-e29b-41d4-a716-446655440000', '013_002', '013', 'Interior medium', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000d', '550e8400-e29b-41d4-a716-446655440000', '013_003', '013', 'Interior close-up', '2026-01-15 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000e', '550e8400-e29b-41d4-a716-446655440000', '014_001', '014', 'Exterior establishing', '2026-01-16 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000f', '550e8400-e29b-41d4-a716-446655440000', '014_002', '014', 'Exterior medium', '2026-01-16 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440000', '014_003', '014', 'Exterior close-up', '2026-01-16 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440000', '014_004', '014', 'Exterior two-shot', '2026-01-16 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440000', '015_001', '015', 'Dialogue scene A', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440000', '015_002', '015', 'Dialogue scene B', '2026-01-16 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440014', '550e8400-e29b-41d4-a716-446655440000', '015_003', '015', 'Dialogue scene C', '2026-01-16 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440015', '550e8400-e29b-41d4-a716-446655440000', '015_004', '015', 'Dialogue scene D', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440016', '550e8400-e29b-41d4-a716-446655440000', '015_005', '015', 'Dialogue scene E', '2026-01-16 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440017', '550e8400-e29b-41d4-a716-446655440000', '016_001', '016', 'Transition shot', '2026-01-16 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440018', '550e8400-e29b-41d4-a716-446655440000', '017_001', '017', 'Climax sequence A', '2026-01-17 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001d', '550e8400-e29b-41d4-a716-446655440000', '018_002', '018', 'Resolution scene B', '2026-01-17 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001e', '550e8400-e29b-41d4-a716-446655440000', '018_003', '018', 'Resolution scene C', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001f', '550e8400-e29b-41d4-a716-446655440000', '019_001', '019', 'Final shot', '2026-01-17 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440000', '019_002', '019', 'Final shot variant', '2026-01-17 14:30:00+00'::timestamptz)
ON CONFLICT (production_id, shot_code) DO NOTHING;

-- Assets: One asset per shot (28 total)
INSERT INTO assets (id, shot_id, production_id, asset_type, clip_name, reel_or_roll, camera_serial, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C001_011_001.mxf', 'A001', 'ALX-001234', '2026-01-15 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C002_011_001A.mxf', 'A001', 'ALX-001234', '2026-01-15 08:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C003_011_001B.mxf', 'A001', 'ALX-001234', '2026-01-15 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440104', '550e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C004_011_002.mxf', 'A001', 'ALX-001234', '2026-01-15 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440105', '550e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C005_011_003.mxf', 'A001', 'ALX-001234', '2026-01-15 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440106', '550e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C006_011_004.mxf', 'A001', 'ALX-001234', '2026-01-15 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440107', '550e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C007_012_001.mxf', 'A001', 'ALX-001234', '2026-01-15 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440108', '550e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C008_012_002.mxf', 'A001', 'ALX-001234', '2026-01-15 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440109', '550e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C009_012_003.mxf', 'A001', 'ALX-001234', '2026-01-15 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544010a', '550e8400-e29b-41d4-a716-44665544000a', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A001C010_012_004.mxf', 'A001', 'ALX-001234', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544010b', '550e8400-e29b-41d4-a716-44665544000b', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C001_013_001.mxf', 'A002', 'ALX-001234', '2026-01-15 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544010c', '550e8400-e29b-41d4-a716-44665544000c', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C002_013_002.mxf', 'A002', 'ALX-001234', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544010d', '550e8400-e29b-41d4-a716-44665544000d', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C003_013_003.mxf', 'A002', 'ALX-001234', '2026-01-15 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544010e', '550e8400-e29b-41d4-a716-44665544000e', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C004_014_001.mxf', 'A002', 'ALX-001234', '2026-01-16 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544010f', '550e8400-e29b-41d4-a716-44665544000f', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C005_014_002.mxf', 'A002', 'ALX-001234', '2026-01-16 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440110', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C006_014_003.mxf', 'A002', 'ALX-001234', '2026-01-16 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440111', '550e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C007_014_004.mxf', 'A002', 'ALX-001234', '2026-01-16 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440112', '550e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C008_015_001.mxf', 'A002', 'ALX-001234', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440113', '550e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C009_015_002.mxf', 'A002', 'ALX-001234', '2026-01-16 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440114', '550e8400-e29b-41d4-a716-446655440014', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A002C010_015_003.mxf', 'A002', 'ALX-001234', '2026-01-16 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440115', '550e8400-e29b-41d4-a716-446655440015', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A003C001_015_004.mxf', 'A003', 'ALX-001234', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440116', '550e8400-e29b-41d4-a716-446655440016', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A003C002_015_005.mxf', 'A003', 'ALX-001234', '2026-01-16 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440117', '550e8400-e29b-41d4-a716-446655440017', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A003C003_016_001.mxf', 'A003', 'ALX-001234', '2026-01-16 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440118', '550e8400-e29b-41d4-a716-446655440018', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A003C004_017_001.mxf', 'A003', 'ALX-001234', '2026-01-17 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544011d', '550e8400-e29b-41d4-a716-44665544001d', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A003C009_018_002.mxf', 'A003', 'ALX-001234', '2026-01-17 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544011e', '550e8400-e29b-41d4-a716-44665544001e', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A003C010_018_003.mxf', 'A003', 'ALX-001234', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544011f', '550e8400-e29b-41d4-a716-44665544001f', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A004C001_019_001.mxf', 'A004', 'ALX-001234', '2026-01-17 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440120', '550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', 'A004C002_019_002.mxf', 'A004', 'ALX-001234', '2026-01-17 14:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Versions: CAMERA_ORIGINAL (28 total)
INSERT INTO versions (id, asset_id, version_type, storage_uri, codec, container, fps, timecode_in, timecode_out, omc_json, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440201', '550e8400-e29b-41d4-a716-446655440101', 'CAMERA_ORIGINAL', 'dam://camera_originals/011_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 21mm T1.5", "focal_length_mm": 21, "aperture": 5.6, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 08:00:00+00", "base_shot_code": "011_001", "human_readable_code": "011_001"}'::jsonb, '2026-01-15 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440202', '550e8400-e29b-41d4-a716-446655440102', 'CAMERA_ORIGINAL', 'dam://camera_originals/011_001A.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 55mm T1.9", "focal_length_mm": 55, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 08:15:00+00", "base_shot_code": "011_001", "human_readable_code": "011_001A", "variant_code": "A"}'::jsonb, '2026-01-15 08:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440203', '550e8400-e29b-41d4-a716-446655440103', 'CAMERA_ORIGINAL', 'dam://camera_originals/011_001B.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 75mm T1.9", "focal_length_mm": 75, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 08:30:00+00", "base_shot_code": "011_001", "human_readable_code": "011_001B", "variant_code": "B"}'::jsonb, '2026-01-15 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440204', '550e8400-e29b-41d4-a716-446655440104', 'CAMERA_ORIGINAL', 'dam://camera_originals/011_002.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 09:00:00+00", "base_shot_code": "011_002", "human_readable_code": "011_002"}'::jsonb, '2026-01-15 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440205', '550e8400-e29b-41d4-a716-446655440105', 'CAMERA_ORIGINAL', 'dam://camera_originals/011_003.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 09:30:00+00", "base_shot_code": "011_003", "human_readable_code": "011_003"}'::jsonb, '2026-01-15 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440206', '550e8400-e29b-41d4-a716-446655440106', 'CAMERA_ORIGINAL', 'dam://camera_originals/011_004.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 10:00:00+00", "base_shot_code": "011_004", "human_readable_code": "011_004"}'::jsonb, '2026-01-15 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440207', '550e8400-e29b-41d4-a716-446655440107', 'CAMERA_ORIGINAL', 'dam://camera_originals/012_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 11:00:00+00", "base_shot_code": "012_001", "human_readable_code": "012_001"}'::jsonb, '2026-01-15 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440208', '550e8400-e29b-41d4-a716-446655440108', 'CAMERA_ORIGINAL', 'dam://camera_originals/012_002.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 11:30:00+00", "base_shot_code": "012_002", "human_readable_code": "012_002"}'::jsonb, '2026-01-15 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440209', '550e8400-e29b-41d4-a716-446655440109', 'CAMERA_ORIGINAL', 'dam://camera_originals/012_003.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 12:00:00+00", "base_shot_code": "012_003", "human_readable_code": "012_003"}'::jsonb, '2026-01-15 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544020a', '550e8400-e29b-41d4-a716-44665544010a', 'CAMERA_ORIGINAL', 'dam://camera_originals/012_004.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 12:30:00+00", "base_shot_code": "012_004", "human_readable_code": "012_004"}'::jsonb, '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544020b', '550e8400-e29b-41d4-a716-44665544010b', 'CAMERA_ORIGINAL', 'dam://camera_originals/013_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 14:00:00+00", "base_shot_code": "013_001", "human_readable_code": "013_001"}'::jsonb, '2026-01-15 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544020c', '550e8400-e29b-41d4-a716-44665544010c', 'CAMERA_ORIGINAL', 'dam://camera_originals/013_002.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 14:30:00+00", "base_shot_code": "013_002", "human_readable_code": "013_002"}'::jsonb, '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544020d', '550e8400-e29b-41d4-a716-44665544010d', 'CAMERA_ORIGINAL', 'dam://camera_originals/013_003.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-15 15:00:00+00", "base_shot_code": "013_003", "human_readable_code": "013_003"}'::jsonb, '2026-01-15 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544020e', '550e8400-e29b-41d4-a716-44665544010e', 'CAMERA_ORIGINAL', 'dam://camera_originals/014_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 18mm T1.9", "focal_length_mm": 18, "aperture": 4.0, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 08:00:00+00", "base_shot_code": "014_001", "human_readable_code": "014_001"}'::jsonb, '2026-01-16 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544020f', '550e8400-e29b-41d4-a716-44665544010f', 'CAMERA_ORIGINAL', 'dam://camera_originals/014_002.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 08:30:00+00", "base_shot_code": "014_002", "human_readable_code": "014_002"}'::jsonb, '2026-01-16 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440210', '550e8400-e29b-41d4-a716-446655440110', 'CAMERA_ORIGINAL', 'dam://camera_originals/014_003.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 09:00:00+00", "base_shot_code": "014_003", "human_readable_code": "014_003"}'::jsonb, '2026-01-16 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440211', '550e8400-e29b-41d4-a716-446655440111', 'CAMERA_ORIGINAL', 'dam://camera_originals/014_004.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 09:30:00+00", "base_shot_code": "014_004", "human_readable_code": "014_004"}'::jsonb, '2026-01-16 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440212', '550e8400-e29b-41d4-a716-446655440112', 'CAMERA_ORIGINAL', 'dam://camera_originals/015_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 11:00:00+00", "base_shot_code": "015_001", "human_readable_code": "015_001"}'::jsonb, '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440213', '550e8400-e29b-41d4-a716-446655440113', 'CAMERA_ORIGINAL', 'dam://camera_originals/015_002.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 11:30:00+00", "base_shot_code": "015_002", "human_readable_code": "015_002"}'::jsonb, '2026-01-16 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440214', '550e8400-e29b-41d4-a716-446655440114', 'CAMERA_ORIGINAL', 'dam://camera_originals/015_003.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 12:00:00+00", "base_shot_code": "015_003", "human_readable_code": "015_003"}'::jsonb, '2026-01-16 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440215', '550e8400-e29b-41d4-a716-446655440115', 'CAMERA_ORIGINAL', 'dam://camera_originals/015_004.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 12:30:00+00", "base_shot_code": "015_004", "human_readable_code": "015_004"}'::jsonb, '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440216', '550e8400-e29b-41d4-a716-446655440116', 'CAMERA_ORIGINAL', 'dam://camera_originals/015_005.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 13:00:00+00", "base_shot_code": "015_005", "human_readable_code": "015_005"}'::jsonb, '2026-01-16 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440217', '550e8400-e29b-41d4-a716-446655440117', 'CAMERA_ORIGINAL', 'dam://camera_originals/016_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-16 14:00:00+00", "base_shot_code": "016_001", "human_readable_code": "016_001"}'::jsonb, '2026-01-16 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440218', '550e8400-e29b-41d4-a716-446655440118', 'CAMERA_ORIGINAL', 'dam://camera_originals/017_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-17 08:00:00+00", "base_shot_code": "017_001", "human_readable_code": "017_001"}'::jsonb, '2026-01-17 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544021d', '550e8400-e29b-41d4-a716-44665544011d', 'CAMERA_ORIGINAL', 'dam://camera_originals/018_002.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-17 11:30:00+00", "base_shot_code": "018_002", "human_readable_code": "018_002"}'::jsonb, '2026-01-17 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544021e', '550e8400-e29b-41d4-a716-44665544011e', 'CAMERA_ORIGINAL', 'dam://camera_originals/018_003.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-17 12:00:00+00", "base_shot_code": "018_003", "human_readable_code": "018_003"}'::jsonb, '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544021f', '550e8400-e29b-41d4-a716-44665544011f', 'CAMERA_ORIGINAL', 'dam://camera_originals/019_001.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-17 14:00:00+00", "base_shot_code": "019_001", "human_readable_code": "019_001"}'::jsonb, '2026-01-17 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440220', '550e8400-e29b-41d4-a716-446655440120', 'CAMERA_ORIGINAL', 'dam://camera_originals/019_002.mxf', 'ARRIRAW', 'MXF', 24.0, '01:00:00:00', '01:00:15:00', '{"camera_make": "ARRI", "camera_model": "ALEXA Mini LF", "serial_number": "ALX-001234", "lens_model": "ARRI Master Prime 35mm T1.3", "focal_length_mm": 35, "aperture": 2.8, "iso": 800, "frame_rate": 24.0, "resolution": "4448x3096", "codec": "ARRIRAW", "color_space": "ARRI Wide Gamut / LogC4", "timecode_start": "01:00:00:00", "timecode_end": "01:00:15:00", "capture_timestamp": "2026-01-17 14:30:00+00", "base_shot_code": "019_002", "human_readable_code": "019_002"}'::jsonb, '2026-01-17 14:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Versions: HDE_MASTER (28 total, derived from camera originals)
INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440301', '550e8400-e29b-41d4-a716-446655440101', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440201', 'dam://hde_masters/011_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440302', '550e8400-e29b-41d4-a716-446655440102', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440202', 'dam://hde_masters/011_001A.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 11:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440303', '550e8400-e29b-41d4-a716-446655440103', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440203', 'dam://hde_masters/011_001B.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440304', '550e8400-e29b-41d4-a716-446655440104', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440204', 'dam://hde_masters/011_002.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440305', '550e8400-e29b-41d4-a716-446655440105', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440205', 'dam://hde_masters/011_003.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440306', '550e8400-e29b-41d4-a716-446655440106', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440206', 'dam://hde_masters/011_004.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440307', '550e8400-e29b-41d4-a716-446655440107', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440207', 'dam://hde_masters/012_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440308', '550e8400-e29b-41d4-a716-446655440108', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440208', 'dam://hde_masters/012_002.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440309', '550e8400-e29b-41d4-a716-446655440109', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440209', 'dam://hde_masters/012_003.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030a', '550e8400-e29b-41d4-a716-44665544010a', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544020a', 'dam://hde_masters/012_004.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030b', '550e8400-e29b-41d4-a716-44665544010b', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544020b', 'dam://hde_masters/013_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030c', '550e8400-e29b-41d4-a716-44665544010c', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544020c', 'dam://hde_masters/013_002.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030d', '550e8400-e29b-41d4-a716-44665544010d', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544020d', 'dam://hde_masters/013_003.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-15 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030e', '550e8400-e29b-41d4-a716-44665544010e', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544020e', 'dam://hde_masters/014_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030f', '550e8400-e29b-41d4-a716-44665544010f', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544020f', 'dam://hde_masters/014_002.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440310', '550e8400-e29b-41d4-a716-446655440110', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440210', 'dam://hde_masters/014_003.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440311', '550e8400-e29b-41d4-a716-446655440111', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440211', 'dam://hde_masters/014_004.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440312', '550e8400-e29b-41d4-a716-446655440112', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440212', 'dam://hde_masters/015_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440313', '550e8400-e29b-41d4-a716-446655440113', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440213', 'dam://hde_masters/015_002.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 13:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440314', '550e8400-e29b-41d4-a716-446655440114', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440214', 'dam://hde_masters/015_003.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440315', '550e8400-e29b-41d4-a716-446655440115', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440215', 'dam://hde_masters/015_004.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 16:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440316', '550e8400-e29b-41d4-a716-446655440116', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440216', 'dam://hde_masters/015_005.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440317', '550e8400-e29b-41d4-a716-446655440117', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440217', 'dam://hde_masters/016_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-16 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440318', '550e8400-e29b-41d4-a716-446655440118', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440218', 'dam://hde_masters/017_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544031d', '550e8400-e29b-41d4-a716-44665544011d', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544021d', 'dam://hde_masters/018_002.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544031e', '550e8400-e29b-41d4-a716-44665544011e', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544021e', 'dam://hde_masters/018_003.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544031f', '550e8400-e29b-41d4-a716-44665544011f', 'HDE_MASTER', '550e8400-e29b-41d4-a716-44665544021f', 'dam://hde_masters/019_001.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440320', '550e8400-e29b-41d4-a716-446655440120', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440220', 'dam://hde_masters/019_002.mov', 'ProRes 422 HQ', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 17:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Versions: DAILIES_PROXY (28 total, derived from HDE masters)
INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, omc_json, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440401', '550e8400-e29b-41d4-a716-446655440101', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440301', 'dam://dailies/011_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440402', '550e8400-e29b-41d4-a716-446655440102', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440302', 'dam://dailies/011_001A.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 17:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440403', '550e8400-e29b-41d4-a716-446655440103', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440303', 'dam://dailies/011_001B.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440404', '550e8400-e29b-41d4-a716-446655440104', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440304', 'dam://dailies/011_002.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 20:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440405', '550e8400-e29b-41d4-a716-446655440105', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440305', 'dam://dailies/011_003.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 21:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440406', '550e8400-e29b-41d4-a716-446655440106', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440306', 'dam://dailies/011_004.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 18:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440407', '550e8400-e29b-41d4-a716-446655440107', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440307', 'dam://dailies/012_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 20:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440408', '550e8400-e29b-41d4-a716-446655440108', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440308', 'dam://dailies/012_002.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 21:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440409', '550e8400-e29b-41d4-a716-446655440109', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440309', 'dam://dailies/012_003.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 23:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040a', '550e8400-e29b-41d4-a716-44665544010a', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544030a', 'dam://dailies/012_004.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 00:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040b', '550e8400-e29b-41d4-a716-44665544010b', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544030b', 'dam://dailies/013_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040c', '550e8400-e29b-41d4-a716-44665544010c', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544030c', 'dam://dailies/013_002.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-15 23:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040d', '550e8400-e29b-41d4-a716-44665544010d', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544030d', 'dam://dailies/013_003.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 01:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040e', '550e8400-e29b-41d4-a716-44665544010e', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544030e', 'dam://dailies/014_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 19:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040f', '550e8400-e29b-41d4-a716-44665544010f', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544030f', 'dam://dailies/014_002.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 20:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440410', '550e8400-e29b-41d4-a716-446655440110', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440310', 'dam://dailies/014_003.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440411', '550e8400-e29b-41d4-a716-446655440111', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440311', 'dam://dailies/014_004.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440412', '550e8400-e29b-41d4-a716-446655440112', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440312', 'dam://dailies/015_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 21:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440413', '550e8400-e29b-41d4-a716-446655440113', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440313', 'dam://dailies/015_002.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 22:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440414', '550e8400-e29b-41d4-a716-446655440114', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440314', 'dam://dailies/015_003.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-17 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440415', '550e8400-e29b-41d4-a716-446655440115', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440315', 'dam://dailies/015_004.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 20:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440416', '550e8400-e29b-41d4-a716-446655440116', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440316', 'dam://dailies/015_005.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-16 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440417', '550e8400-e29b-41d4-a716-446655440117', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440317', 'dam://dailies/016_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-17 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440418', '550e8400-e29b-41d4-a716-446655440118', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440318', 'dam://dailies/017_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', NULL, '2026-01-17 19:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544041d', '550e8400-e29b-41d4-a716-44665544011d', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544031d', 'dam://dailies/018_002.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', '{"editorial_notes": "coverage not used in final cut"}'::jsonb, '2026-01-17 22:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544041e', '550e8400-e29b-41d4-a716-44665544011e', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544031e', 'dam://dailies/018_003.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', '{"editorial_status": "not_cut"}'::jsonb, '2026-01-18 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544041f', '550e8400-e29b-41d4-a716-44665544011f', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-44665544031f', 'dam://dailies/019_001.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', '{"editorial_notes": "performance superseded by alternate take"}'::jsonb, '2026-01-17 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440420', '550e8400-e29b-41d4-a716-446655440120', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440320', 'dam://dailies/019_002.mp4', 'H.264', 'MP4', 24.0, '01:00:00:00', '01:00:15:00', '{"editorial_status": "not_cut"}'::jsonb, '2026-01-17 23:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Versions: EDIT_EXPORT (24 total, 4 shots blocked)
INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440101', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440401', 'dam://edit_exports/011_001.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440502', '550e8400-e29b-41d4-a716-446655440102', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440402', 'dam://edit_exports/011_001A.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-18 08:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440503', '550e8400-e29b-41d4-a716-446655440103', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440403', 'dam://edit_exports/011_001B.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-19 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440504', '550e8400-e29b-41d4-a716-446655440104', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440404', 'dam://edit_exports/011_002.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-20 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440505', '550e8400-e29b-41d4-a716-446655440105', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440405', 'dam://edit_exports/011_003.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440506', '550e8400-e29b-41d4-a716-446655440106', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440406', 'dam://edit_exports/011_004.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-18 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440507', '550e8400-e29b-41d4-a716-446655440107', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440407', 'dam://edit_exports/012_001.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-19 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440508', '550e8400-e29b-41d4-a716-446655440108', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440408', 'dam://edit_exports/012_002.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-20 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440509', '550e8400-e29b-41d4-a716-446655440109', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440409', 'dam://edit_exports/012_003.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050a', '550e8400-e29b-41d4-a716-44665544010a', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-44665544040a', 'dam://edit_exports/012_004.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-18 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050b', '550e8400-e29b-41d4-a716-44665544010b', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-44665544040b', 'dam://edit_exports/013_001.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-19 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050c', '550e8400-e29b-41d4-a716-44665544010c', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-44665544040c', 'dam://edit_exports/013_002.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-20 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050d', '550e8400-e29b-41d4-a716-44665544010d', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-44665544040d', 'dam://edit_exports/013_003.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-17 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050e', '550e8400-e29b-41d4-a716-44665544010e', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-44665544040e', 'dam://edit_exports/014_001.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-19 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050f', '550e8400-e29b-41d4-a716-44665544010f', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-44665544040f', 'dam://edit_exports/014_002.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-20 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440510', '550e8400-e29b-41d4-a716-446655440110', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440410', 'dam://edit_exports/014_003.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-21 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440511', '550e8400-e29b-41d4-a716-446655440111', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440411', 'dam://edit_exports/014_004.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-18 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440512', '550e8400-e29b-41d4-a716-446655440112', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440412', 'dam://edit_exports/015_001.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-19 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440513', '550e8400-e29b-41d4-a716-446655440113', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440413', 'dam://edit_exports/015_002.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-20 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440514', '550e8400-e29b-41d4-a716-446655440114', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440414', 'dam://edit_exports/015_003.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-21 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440515', '550e8400-e29b-41d4-a716-446655440115', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440415', 'dam://edit_exports/015_004.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-18 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440516', '550e8400-e29b-41d4-a716-446655440116', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440416', 'dam://edit_exports/015_005.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-19 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440517', '550e8400-e29b-41d4-a716-446655440117', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440417', 'dam://edit_exports/016_001.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-20 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440518', '550e8400-e29b-41d4-a716-446655440118', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440418', 'dam://edit_exports/017_001.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '2026-01-22 08:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Versions: Rework EDIT_EXPORT (4 rework cases)
INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, creative_context, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440101', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440501', 'dam://edit_exports/011_001_v2.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '{"rework_type": "editorial", "reason": "Editorial re-cut for pacing"}'::jsonb, '2026-01-20 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440602', '550e8400-e29b-41d4-a716-446655440106', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440506', 'dam://edit_exports/011_004_v2.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '{"rework_type": "editorial", "reason": "Editorial re-cut for continuity"}'::jsonb, '2026-01-21 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440603', '550e8400-e29b-41d4-a716-446655440107', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440507', 'dam://edit_exports/012_001_v2.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '{"rework_type": "vfx", "reason": "VFX revision requested"}'::jsonb, '2026-01-22 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440604', '550e8400-e29b-41d4-a716-44665544010e', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-44665544050e', 'dam://edit_exports/014_001_v2.mov', 'ProRes 422', 'MOV', 24.0, '01:00:00:00', '01:00:15:00', '{"rework_type": "creative", "reason": "Director notes - creative rework"}'::jsonb, '2026-01-24 08:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Version Lineage: Explicit edges for all derivations
INSERT INTO version_lineage (derived_version_id, source_version_id, transform_type, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440301', '550e8400-e29b-41d4-a716-446655440201', 'HDE_TRANSCODE', '2026-01-15 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440401', '550e8400-e29b-41d4-a716-446655440301', 'DAILIES_ENCODE', '2026-01-15 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440401', 'EDIT_EXPORT', '2026-01-17 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440501', 'REWORK_EDITORIAL', '2026-01-20 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440302', '550e8400-e29b-41d4-a716-446655440202', 'HDE_TRANSCODE', '2026-01-15 11:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440402', '550e8400-e29b-41d4-a716-446655440302', 'DAILIES_ENCODE', '2026-01-15 17:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440502', '550e8400-e29b-41d4-a716-446655440402', 'EDIT_EXPORT', '2026-01-18 08:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440303', '550e8400-e29b-41d4-a716-446655440203', 'HDE_TRANSCODE', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440403', '550e8400-e29b-41d4-a716-446655440303', 'DAILIES_ENCODE', '2026-01-15 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440503', '550e8400-e29b-41d4-a716-446655440403', 'EDIT_EXPORT', '2026-01-19 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440304', '550e8400-e29b-41d4-a716-446655440204', 'HDE_TRANSCODE', '2026-01-15 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440404', '550e8400-e29b-41d4-a716-446655440304', 'DAILIES_ENCODE', '2026-01-15 20:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440504', '550e8400-e29b-41d4-a716-446655440404', 'EDIT_EXPORT', '2026-01-20 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440305', '550e8400-e29b-41d4-a716-446655440205', 'HDE_TRANSCODE', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440405', '550e8400-e29b-41d4-a716-446655440305', 'DAILIES_ENCODE', '2026-01-15 21:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440505', '550e8400-e29b-41d4-a716-446655440405', 'EDIT_EXPORT', '2026-01-17 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440306', '550e8400-e29b-41d4-a716-446655440206', 'HDE_TRANSCODE', '2026-01-15 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440406', '550e8400-e29b-41d4-a716-446655440306', 'DAILIES_ENCODE', '2026-01-15 18:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440506', '550e8400-e29b-41d4-a716-446655440406', 'EDIT_EXPORT', '2026-01-18 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440602', '550e8400-e29b-41d4-a716-446655440506', 'REWORK_EDITORIAL', '2026-01-21 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440307', '550e8400-e29b-41d4-a716-446655440207', 'HDE_TRANSCODE', '2026-01-15 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440407', '550e8400-e29b-41d4-a716-446655440307', 'DAILIES_ENCODE', '2026-01-15 20:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440507', '550e8400-e29b-41d4-a716-446655440407', 'EDIT_EXPORT', '2026-01-19 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440603', '550e8400-e29b-41d4-a716-446655440507', 'REWORK_VFX', '2026-01-22 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440308', '550e8400-e29b-41d4-a716-446655440208', 'HDE_TRANSCODE', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440408', '550e8400-e29b-41d4-a716-446655440308', 'DAILIES_ENCODE', '2026-01-15 21:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440508', '550e8400-e29b-41d4-a716-446655440408', 'EDIT_EXPORT', '2026-01-20 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440309', '550e8400-e29b-41d4-a716-446655440209', 'HDE_TRANSCODE', '2026-01-15 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440409', '550e8400-e29b-41d4-a716-446655440309', 'DAILIES_ENCODE', '2026-01-15 23:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440509', '550e8400-e29b-41d4-a716-446655440409', 'EDIT_EXPORT', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030a', '550e8400-e29b-41d4-a716-44665544020a', 'HDE_TRANSCODE', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040a', '550e8400-e29b-41d4-a716-44665544030a', 'DAILIES_ENCODE', '2026-01-16 00:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050a', '550e8400-e29b-41d4-a716-44665544040a', 'EDIT_EXPORT', '2026-01-18 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030b', '550e8400-e29b-41d4-a716-44665544020b', 'HDE_TRANSCODE', '2026-01-15 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040b', '550e8400-e29b-41d4-a716-44665544030b', 'DAILIES_ENCODE', '2026-01-15 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050b', '550e8400-e29b-41d4-a716-44665544040b', 'EDIT_EXPORT', '2026-01-19 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030c', '550e8400-e29b-41d4-a716-44665544020c', 'HDE_TRANSCODE', '2026-01-15 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040c', '550e8400-e29b-41d4-a716-44665544030c', 'DAILIES_ENCODE', '2026-01-15 23:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050c', '550e8400-e29b-41d4-a716-44665544040c', 'EDIT_EXPORT', '2026-01-20 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030d', '550e8400-e29b-41d4-a716-44665544020d', 'HDE_TRANSCODE', '2026-01-15 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040d', '550e8400-e29b-41d4-a716-44665544030d', 'DAILIES_ENCODE', '2026-01-16 01:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050d', '550e8400-e29b-41d4-a716-44665544040d', 'EDIT_EXPORT', '2026-01-17 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030e', '550e8400-e29b-41d4-a716-44665544020e', 'HDE_TRANSCODE', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040e', '550e8400-e29b-41d4-a716-44665544030e', 'DAILIES_ENCODE', '2026-01-16 19:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050e', '550e8400-e29b-41d4-a716-44665544040e', 'EDIT_EXPORT', '2026-01-19 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440604', '550e8400-e29b-41d4-a716-44665544050e', 'REWORK_CREATIVE', '2026-01-24 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544030f', '550e8400-e29b-41d4-a716-44665544020f', 'HDE_TRANSCODE', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544040f', '550e8400-e29b-41d4-a716-44665544030f', 'DAILIES_ENCODE', '2026-01-16 20:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544050f', '550e8400-e29b-41d4-a716-44665544040f', 'EDIT_EXPORT', '2026-01-20 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440310', '550e8400-e29b-41d4-a716-446655440210', 'HDE_TRANSCODE', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440410', '550e8400-e29b-41d4-a716-446655440310', 'DAILIES_ENCODE', '2026-01-16 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440510', '550e8400-e29b-41d4-a716-446655440410', 'EDIT_EXPORT', '2026-01-21 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440311', '550e8400-e29b-41d4-a716-446655440211', 'HDE_TRANSCODE', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440411', '550e8400-e29b-41d4-a716-446655440311', 'DAILIES_ENCODE', '2026-01-16 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440511', '550e8400-e29b-41d4-a716-446655440411', 'EDIT_EXPORT', '2026-01-18 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440312', '550e8400-e29b-41d4-a716-446655440212', 'HDE_TRANSCODE', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440412', '550e8400-e29b-41d4-a716-446655440312', 'DAILIES_ENCODE', '2026-01-16 21:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440512', '550e8400-e29b-41d4-a716-446655440412', 'EDIT_EXPORT', '2026-01-19 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440313', '550e8400-e29b-41d4-a716-446655440213', 'HDE_TRANSCODE', '2026-01-16 13:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440413', '550e8400-e29b-41d4-a716-446655440313', 'DAILIES_ENCODE', '2026-01-16 22:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440513', '550e8400-e29b-41d4-a716-446655440413', 'EDIT_EXPORT', '2026-01-20 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440314', '550e8400-e29b-41d4-a716-446655440214', 'HDE_TRANSCODE', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440414', '550e8400-e29b-41d4-a716-446655440314', 'DAILIES_ENCODE', '2026-01-17 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440514', '550e8400-e29b-41d4-a716-446655440414', 'EDIT_EXPORT', '2026-01-21 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440315', '550e8400-e29b-41d4-a716-446655440215', 'HDE_TRANSCODE', '2026-01-16 16:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440415', '550e8400-e29b-41d4-a716-446655440315', 'DAILIES_ENCODE', '2026-01-16 20:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440515', '550e8400-e29b-41d4-a716-446655440415', 'EDIT_EXPORT', '2026-01-18 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440316', '550e8400-e29b-41d4-a716-446655440216', 'HDE_TRANSCODE', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440416', '550e8400-e29b-41d4-a716-446655440316', 'DAILIES_ENCODE', '2026-01-16 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440516', '550e8400-e29b-41d4-a716-446655440416', 'EDIT_EXPORT', '2026-01-19 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440317', '550e8400-e29b-41d4-a716-446655440217', 'HDE_TRANSCODE', '2026-01-16 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440417', '550e8400-e29b-41d4-a716-446655440317', 'DAILIES_ENCODE', '2026-01-17 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440517', '550e8400-e29b-41d4-a716-446655440417', 'EDIT_EXPORT', '2026-01-20 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440318', '550e8400-e29b-41d4-a716-446655440218', 'HDE_TRANSCODE', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440418', '550e8400-e29b-41d4-a716-446655440318', 'DAILIES_ENCODE', '2026-01-17 19:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440518', '550e8400-e29b-41d4-a716-446655440418', 'EDIT_EXPORT', '2026-01-22 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544031d', '550e8400-e29b-41d4-a716-44665544021d', 'HDE_TRANSCODE', '2026-01-17 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544041d', '550e8400-e29b-41d4-a716-44665544031d', 'DAILIES_ENCODE', '2026-01-17 22:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544031e', '550e8400-e29b-41d4-a716-44665544021e', 'HDE_TRANSCODE', '2026-01-17 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544041e', '550e8400-e29b-41d4-a716-44665544031e', 'DAILIES_ENCODE', '2026-01-18 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544031f', '550e8400-e29b-41d4-a716-44665544021f', 'HDE_TRANSCODE', '2026-01-17 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544041f', '550e8400-e29b-41d4-a716-44665544031f', 'DAILIES_ENCODE', '2026-01-17 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440320', '550e8400-e29b-41d4-a716-446655440220', 'HDE_TRANSCODE', '2026-01-17 17:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440420', '550e8400-e29b-41d4-a716-446655440320', 'DAILIES_ENCODE', '2026-01-17 23:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Events: CAPTURE (28 total)
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440201', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440002', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440202', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 08:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440003', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440203', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440004', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440204', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440005', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440205', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440206', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440207', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440008', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440208', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440009', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440209', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000a', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544020a', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000b', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544020b', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000c', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544020c', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000d', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544020d', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-15 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000e', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544020e', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000f', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544020f', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440010', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440210', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440011', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440211', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440012', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440212', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440013', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440213', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440014', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440214', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440015', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440215', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440016', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440216', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440017', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440217', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-16 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440018', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440218', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-17 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001d', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544021d', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-17 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001e', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544021e', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001f', 'CAPTURE', '550e8400-e29b-41d4-a716-44665544021f', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-17 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440020', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440220', 'Camera Operator', 'ARRI ALEXA Mini LF', '2026-01-17 14:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Events: HDE_TRANSCODE (28 total)
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440301', 'DIT', 'Offload Service', '2026-01-15 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440002', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440302', 'DIT', 'Offload Service', '2026-01-15 11:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440003', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440303', 'DIT', 'Offload Service', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440004', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440304', 'DIT', 'Offload Service', '2026-01-15 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440005', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440305', 'DIT', 'Offload Service', '2026-01-15 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440306', 'DIT', 'Offload Service', '2026-01-15 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440307', 'DIT', 'Offload Service', '2026-01-15 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440008', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440308', 'DIT', 'Offload Service', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440009', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440309', 'DIT', 'Offload Service', '2026-01-15 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000a', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544030a', 'DIT', 'Offload Service', '2026-01-15 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000b', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544030b', 'DIT', 'Offload Service', '2026-01-15 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000c', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544030c', 'DIT', 'Offload Service', '2026-01-15 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000d', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544030d', 'DIT', 'Offload Service', '2026-01-15 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000e', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544030e', 'DIT', 'Offload Service', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000f', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544030f', 'DIT', 'Offload Service', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440010', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440310', 'DIT', 'Offload Service', '2026-01-16 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440011', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440311', 'DIT', 'Offload Service', '2026-01-16 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440012', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440312', 'DIT', 'Offload Service', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440013', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440313', 'DIT', 'Offload Service', '2026-01-16 13:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440014', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440314', 'DIT', 'Offload Service', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440015', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440315', 'DIT', 'Offload Service', '2026-01-16 16:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440016', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440316', 'DIT', 'Offload Service', '2026-01-16 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440017', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440317', 'DIT', 'Offload Service', '2026-01-16 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440018', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440318', 'DIT', 'Offload Service', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001d', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544031d', 'DIT', 'Offload Service', '2026-01-17 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001e', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544031e', 'DIT', 'Offload Service', '2026-01-17 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001f', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-44665544031f', 'DIT', 'Offload Service', '2026-01-17 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440020', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440320', 'DIT', 'Offload Service', '2026-01-17 17:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Events: DAILIES_PUBLISHED (28 total)
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440401', 'Dailies Operator', 'Dailies Service', '2026-01-15 16:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440002', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440402', 'Dailies Operator', 'Dailies Service', '2026-01-15 17:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440003', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440403', 'Dailies Operator', 'Dailies Service', '2026-01-15 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440004', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440404', 'Dailies Operator', 'Dailies Service', '2026-01-15 20:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440005', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440405', 'Dailies Operator', 'Dailies Service', '2026-01-15 21:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440406', 'Dailies Operator', 'Dailies Service', '2026-01-15 18:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440407', 'Dailies Operator', 'Dailies Service', '2026-01-15 20:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440008', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440408', 'Dailies Operator', 'Dailies Service', '2026-01-15 21:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440009', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440409', 'Dailies Operator', 'Dailies Service', '2026-01-15 23:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000a', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544040a', 'Dailies Operator', 'Dailies Service', '2026-01-16 00:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000b', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544040b', 'Dailies Operator', 'Dailies Service', '2026-01-15 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000c', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544040c', 'Dailies Operator', 'Dailies Service', '2026-01-15 23:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000d', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544040d', 'Dailies Operator', 'Dailies Service', '2026-01-16 01:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000e', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544040e', 'Dailies Operator', 'Dailies Service', '2026-01-16 19:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000f', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544040f', 'Dailies Operator', 'Dailies Service', '2026-01-16 20:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440010', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440410', 'Dailies Operator', 'Dailies Service', '2026-01-16 17:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440011', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440411', 'Dailies Operator', 'Dailies Service', '2026-01-16 18:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440012', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440412', 'Dailies Operator', 'Dailies Service', '2026-01-16 21:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440013', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440413', 'Dailies Operator', 'Dailies Service', '2026-01-16 22:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440014', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440414', 'Dailies Operator', 'Dailies Service', '2026-01-17 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440015', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440415', 'Dailies Operator', 'Dailies Service', '2026-01-16 20:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440016', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440416', 'Dailies Operator', 'Dailies Service', '2026-01-16 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440017', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440417', 'Dailies Operator', 'Dailies Service', '2026-01-17 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440018', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440418', 'Dailies Operator', 'Dailies Service', '2026-01-17 19:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001d', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544041d', 'Dailies Operator', 'Dailies Service', '2026-01-17 22:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001e', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544041e', 'Dailies Operator', 'Dailies Service', '2026-01-18 00:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544001f', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-44665544041f', 'Dailies Operator', 'Dailies Service', '2026-01-17 22:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440020', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440420', 'Dailies Operator', 'Dailies Service', '2026-01-17 23:30:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Events: EDIT_EXPORT_CREATED (24 total, 4 shots blocked)
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440501', 'Editor', 'Avid Media Composer', '2026-01-17 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440002', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440502', 'Editor', 'Avid Media Composer', '2026-01-18 08:15:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440003', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440503', 'Editor', 'Avid Media Composer', '2026-01-19 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440004', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440504', 'Editor', 'Avid Media Composer', '2026-01-20 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440005', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440505', 'Editor', 'Avid Media Composer', '2026-01-17 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440506', 'Editor', 'Avid Media Composer', '2026-01-18 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440507', 'Editor', 'Avid Media Composer', '2026-01-19 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440008', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440508', 'Editor', 'Avid Media Composer', '2026-01-20 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440009', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440509', 'Editor', 'Avid Media Composer', '2026-01-17 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000a', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-44665544050a', 'Editor', 'Avid Media Composer', '2026-01-18 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000b', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-44665544050b', 'Editor', 'Avid Media Composer', '2026-01-19 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000c', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-44665544050c', 'Editor', 'Avid Media Composer', '2026-01-20 14:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000d', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-44665544050d', 'Editor', 'Avid Media Composer', '2026-01-17 15:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000e', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-44665544050e', 'Editor', 'Avid Media Composer', '2026-01-19 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000f', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-44665544050f', 'Editor', 'Avid Media Composer', '2026-01-20 08:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440010', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440510', 'Editor', 'Avid Media Composer', '2026-01-21 09:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440011', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440511', 'Editor', 'Avid Media Composer', '2026-01-18 09:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440012', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440512', 'Editor', 'Avid Media Composer', '2026-01-19 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440013', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440513', 'Editor', 'Avid Media Composer', '2026-01-20 11:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440014', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440514', 'Editor', 'Avid Media Composer', '2026-01-21 12:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440015', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440515', 'Editor', 'Avid Media Composer', '2026-01-18 12:30:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440016', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440516', 'Editor', 'Avid Media Composer', '2026-01-19 13:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440017', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440517', 'Editor', 'Avid Media Composer', '2026-01-20 14:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440018', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440518', 'Editor', 'Avid Media Composer', '2026-01-22 08:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Events: Rework EDIT_EXPORT_CREATED (4 rework cases)
INSERT INTO events (shot_id, event_type, version_id, actor, tool, details, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440601', 'Editor', 'Avid Media Composer', '{"rework_type": "editorial", "reason": "Editorial re-cut for pacing"}'::jsonb, '2026-01-20 08:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440602', 'Editor', 'Avid Media Composer', '{"rework_type": "editorial", "reason": "Editorial re-cut for continuity"}'::jsonb, '2026-01-21 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440603', 'Editor', 'Avid Media Composer', '{"rework_type": "vfx", "reason": "VFX revision requested"}'::jsonb, '2026-01-22 11:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000e', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440604', 'Editor', 'Avid Media Composer', '{"rework_type": "creative", "reason": "Director notes - creative rework"}'::jsonb, '2026-01-24 08:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Packages: TURNOVER
INSERT INTO packages (id, production_id, package_type, label, vendor, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440000', 'TURNOVER', 'VFX Turnover - Scenes 011-015', 'VFX Vendor Alpha', '2026-01-20 10:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Package Members: TURNOVER (12 shots)
INSERT INTO package_members (package_id, version_id, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440501', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440502', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440503', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440504', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440505', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440506', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440507', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440508', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-446655440509', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-44665544050a', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-44665544050b', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440701', '550e8400-e29b-41d4-a716-44665544050c', '2026-01-20 10:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Events: TURNOVER_DELIVERED
INSERT INTO events (shot_id, event_type, package_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440002', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440003', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440004', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440005', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440008', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440009', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000a', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000b', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-44665544000c', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440701', 'Post Supervisor', 'Package Service', '2026-01-20 10:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Packages: ARCHIVE
INSERT INTO packages (id, production_id, package_type, label, vendor, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440000', 'ARCHIVE', 'Archive Package - Initial Deliverables', NULL, '2026-01-20 10:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Package Members: ARCHIVE (8 existing + 12 from TURNOVER so ARCHIVE is superset of TURNOVER)
INSERT INTO package_members (package_id, version_id, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440301', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440302', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440303', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440304', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440305', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440306', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440307', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440308', '2026-01-20 10:00:00+00'::timestamptz),
    -- TURNOVER members (EDIT_EXPORT versions) added so ARCHIVE >= TURNOVER for EXFTR
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440501', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440502', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440503', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440504', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440505', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440506', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440507', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440508', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-446655440509', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-44665544050a', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-44665544050b', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440702', '550e8400-e29b-41d4-a716-44665544050c', '2026-01-20 10:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;

-- Events: ARCHIVED
INSERT INTO events (shot_id, event_type, package_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440002', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440003', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440004', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440005', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440006', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440007', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz),
    ('550e8400-e29b-41d4-a716-446655440008', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440702', 'Archive Operator', 'Archive Service', '2026-01-20 10:00:00+00'::timestamptz)
ON CONFLICT DO NOTHING;
