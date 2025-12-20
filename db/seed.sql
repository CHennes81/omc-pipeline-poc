-- Production Lineage Concierge POC - Seed Data
-- Phase 1: Deterministic demo dataset
-- This seed is idempotent: safe to run multiple times

-- Clear existing data (optional, for clean reset)
-- Uncomment the following lines if you want a full reset:
-- TRUNCATE TABLE events, package_members, packages, version_lineage, versions, assets, shots, productions CASCADE;

-- Production
INSERT INTO productions (id, code, title, created_at)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'EXFTR', 'Example Feature (Demo)', CURRENT_TIMESTAMP)
ON CONFLICT (code) DO UPDATE SET title = EXCLUDED.title;

-- Shots (at least 3 shots, with one blocked case)
INSERT INTO shots (id, production_id, shot_code, scene, description, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', '011_021', '011', 'Wide establishing shot', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', '011_022', '011', 'Medium two-shot', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', '012_010', '012', 'Close-up reaction', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440000', '012_011', '012', 'Over-shoulder dialogue', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440000', '013_015', '013', 'Action sequence', CURRENT_TIMESTAMP)
ON CONFLICT (production_id, shot_code) DO NOTHING;

-- Assets (one asset per shot for simplicity)
INSERT INTO assets (id, shot_id, production_id, asset_type, clip_name, reel_or_roll, camera_serial, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', '10254613-uhd_4096_2160_25fps.mp4', 'A001', 'CAM001', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', '13967595_3840_2160_25fps.mp4', 'A001', 'CAM001', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', '14542855_3840_2160_60fps.mp4', 'A002', 'CAM002', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440104', '550e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', '14646171_1920_1080_25fps.mp4', 'A002', 'CAM002', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440105', '550e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440000', 'PICTURE', '14663025_3840_2160_60fps.mp4', 'A003', 'CAM001', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Versions: Camera Originals
INSERT INTO versions (id, asset_id, version_type, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440201', '550e8400-e29b-41d4-a716-446655440101', 'CAMERA_ORIGINAL', 'dam://camera_originals/10254613-uhd_4096_2160_25fps.mp4', 'H.264', 'MP4', 25.0, '01:00:00:00', '01:00:10:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440202', '550e8400-e29b-41d4-a716-446655440102', 'CAMERA_ORIGINAL', 'dam://camera_originals/13967595_3840_2160_25fps.mp4', 'H.264', 'MP4', 25.0, '01:00:00:00', '01:00:08:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440203', '550e8400-e29b-41d4-a716-446655440103', 'CAMERA_ORIGINAL', 'dam://camera_originals/14542855_3840_2160_60fps.mp4', 'H.264', 'MP4', 60.0, '01:00:00:00', '01:00:12:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440204', '550e8400-e29b-41d4-a716-446655440104', 'CAMERA_ORIGINAL', 'dam://camera_originals/14646171_1920_1080_25fps.mp4', 'H.264', 'MP4', 25.0, '01:00:00:00', '01:00:15:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440205', '550e8400-e29b-41d4-a716-446655440105', 'CAMERA_ORIGINAL', 'dam://camera_originals/14663025_3840_2160_60fps.mp4', 'H.264', 'MP4', 60.0, '01:00:00:00', '01:00:20:00', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Versions: HDE Masters (derived from camera originals)
INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440301', '550e8400-e29b-41d4-a716-446655440101', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440201', 'dam://hde_masters/10254613-uhd_4096_2160_25fps.mov', 'ProRes 422 HQ', 'MOV', 25.0, '01:00:00:00', '01:00:10:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440302', '550e8400-e29b-41d4-a716-446655440102', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440202', 'dam://hde_masters/13967595_3840_2160_25fps.mov', 'ProRes 422 HQ', 'MOV', 25.0, '01:00:00:00', '01:00:08:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440303', '550e8400-e29b-41d4-a716-446655440103', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440203', 'dam://hde_masters/14542855_3840_2160_60fps.mov', 'ProRes 422 HQ', 'MOV', 60.0, '01:00:00:00', '01:00:12:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440304', '550e8400-e29b-41d4-a716-446655440104', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440204', 'dam://hde_masters/14646171_1920_1080_25fps.mov', 'ProRes 422 HQ', 'MOV', 25.0, '01:00:00:00', '01:00:15:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440305', '550e8400-e29b-41d4-a716-446655440105', 'HDE_MASTER', '550e8400-e29b-41d4-a716-446655440205', 'dam://hde_masters/14663025_3840_2160_60fps.mov', 'ProRes 422 HQ', 'MOV', 60.0, '01:00:00:00', '01:00:20:00', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Versions: Dailies Proxies (derived from HDE masters)
INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440401', '550e8400-e29b-41d4-a716-446655440101', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440301', 'dam://dailies/10254613-uhd_4096_2160_25fps.mp4', 'H.264', 'MP4', 25.0, '01:00:00:00', '01:00:10:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440402', '550e8400-e29b-41d4-a716-446655440102', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440302', 'dam://dailies/13967595_3840_2160_25fps.mp4', 'H.264', 'MP4', 25.0, '01:00:00:00', '01:00:08:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440403', '550e8400-e29b-41d4-a716-446655440103', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440303', 'dam://dailies/14542855_3840_2160_60fps.mp4', 'H.264', 'MP4', 60.0, '01:00:00:00', '01:00:12:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440404', '550e8400-e29b-41d4-a716-446655440104', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440304', 'dam://dailies/14646171_1920_1080_25fps.mp4', 'H.264', 'MP4', 25.0, '01:00:00:00', '01:00:15:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440405', '550e8400-e29b-41d4-a716-446655440105', 'DAILIES_PROXY', '550e8400-e29b-41d4-a716-446655440305', 'dam://dailies/14663025_3840_2160_60fps.mp4', 'H.264', 'MP4', 60.0, '01:00:00:00', '01:00:20:00', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Versions: Edit Exports (only for shots 011_021, 011_022, 012_010 - leaving 012_011 and 013_015 blocked)
INSERT INTO versions (id, asset_id, version_type, derived_from_version_id, storage_uri, codec, container, fps, timecode_in, timecode_out, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440101', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440401', 'dam://edit_exports/10254613-uhd_4096_2160_25fps.mov', 'ProRes 422', 'MOV', 25.0, '01:00:00:00', '01:00:10:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440502', '550e8400-e29b-41d4-a716-446655440102', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440402', 'dam://edit_exports/13967595_3840_2160_25fps.mov', 'ProRes 422', 'MOV', 25.0, '01:00:00:00', '01:00:08:00', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440503', '550e8400-e29b-41d4-a716-446655440103', 'EDIT_EXPORT', '550e8400-e29b-41d4-a716-446655440403', 'dam://edit_exports/14542855_3840_2160_60fps.mov', 'ProRes 422', 'MOV', 60.0, '01:00:00:00', '01:00:12:00', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Version Lineage edges (explicit)
INSERT INTO version_lineage (derived_version_id, source_version_id, transform_type, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440301', '550e8400-e29b-41d4-a716-446655440201', 'HDE_TRANSCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440302', '550e8400-e29b-41d4-a716-446655440202', 'HDE_TRANSCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440303', '550e8400-e29b-41d4-a716-446655440203', 'HDE_TRANSCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440304', '550e8400-e29b-41d4-a716-446655440204', 'HDE_TRANSCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440305', '550e8400-e29b-41d4-a716-446655440205', 'HDE_TRANSCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440401', '550e8400-e29b-41d4-a716-446655440301', 'DAILIES_ENCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440402', '550e8400-e29b-41d4-a716-446655440302', 'DAILIES_ENCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440403', '550e8400-e29b-41d4-a716-446655440303', 'DAILIES_ENCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440404', '550e8400-e29b-41d4-a716-446655440304', 'DAILIES_ENCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440405', '550e8400-e29b-41d4-a716-446655440305', 'DAILIES_ENCODE', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440401', 'EDIT_EXPORT', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440502', '550e8400-e29b-41d4-a716-446655440402', 'EDIT_EXPORT', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440503', '550e8400-e29b-41d4-a716-446655440403', 'EDIT_EXPORT', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Events: CAPTURE
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440201', 'Camera Operator', 'ARRI ALEXA', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    ('550e8400-e29b-41d4-a716-446655440002', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440202', 'Camera Operator', 'ARRI ALEXA', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    ('550e8400-e29b-41d4-a716-446655440003', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440203', 'Camera Operator', 'ARRI ALEXA', CURRENT_TIMESTAMP - INTERVAL '4 days'),
    ('550e8400-e29b-41d4-a716-446655440004', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440204', 'Camera Operator', 'ARRI ALEXA', CURRENT_TIMESTAMP - INTERVAL '4 days'),
    ('550e8400-e29b-41d4-a716-446655440005', 'CAPTURE', '550e8400-e29b-41d4-a716-446655440205', 'Camera Operator', 'ARRI ALEXA', CURRENT_TIMESTAMP - INTERVAL '3 days')
ON CONFLICT DO NOTHING;

-- Events: HDE_TRANSCODE
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440301', 'DIT', 'Offload Service', CURRENT_TIMESTAMP - INTERVAL '4 days'),
    ('550e8400-e29b-41d4-a716-446655440002', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440302', 'DIT', 'Offload Service', CURRENT_TIMESTAMP - INTERVAL '4 days'),
    ('550e8400-e29b-41d4-a716-446655440003', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440303', 'DIT', 'Offload Service', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440004', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440304', 'DIT', 'Offload Service', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440005', 'HDE_TRANSCODE', '550e8400-e29b-41d4-a716-446655440305', 'DIT', 'Offload Service', CURRENT_TIMESTAMP - INTERVAL '2 days')
ON CONFLICT DO NOTHING;

-- Events: DAILIES_PUBLISHED
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440401', 'Dailies Operator', 'Dailies Service', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440002', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440402', 'Dailies Operator', 'Dailies Service', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440003', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440403', 'Dailies Operator', 'Dailies Service', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440004', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440404', 'Dailies Operator', 'Dailies Service', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440005', 'DAILIES_PUBLISHED', '550e8400-e29b-41d4-a716-446655440405', 'Dailies Operator', 'Dailies Service', CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- Events: EDIT_EXPORT_CREATED (only for shots with edit exports)
INSERT INTO events (shot_id, event_type, version_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440501', 'Editor', 'Avid Media Composer', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440002', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440502', 'Editor', 'Avid Media Composer', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440003', 'EDIT_EXPORT_CREATED', '550e8400-e29b-41d4-a716-446655440503', 'Editor', 'Avid Media Composer', CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- Packages: TURNOVER (3 shots)
INSERT INTO packages (id, production_id, package_type, label, vendor, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440000', 'TURNOVER', 'VFX Turnover - Scene 011', 'VFX Vendor Alpha', CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- Package Members: TURNOVER
INSERT INTO package_members (package_id, version_id, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440501', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440502', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440503', CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- Events: TURNOVER_DELIVERED
INSERT INTO events (shot_id, event_type, package_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440601', 'Post Supervisor', 'Package Service', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('550e8400-e29b-41d4-a716-446655440002', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440601', 'Post Supervisor', 'Package Service', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('550e8400-e29b-41d4-a716-446655440003', 'TURNOVER_DELIVERED', '550e8400-e29b-41d4-a716-446655440601', 'Post Supervisor', 'Package Service', CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

-- Packages: ARCHIVE (2 shots)
INSERT INTO packages (id, production_id, package_type, label, vendor, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440602', '550e8400-e29b-41d4-a716-446655440000', 'ARCHIVE', 'Archive Package - Initial Deliverables', NULL, CURRENT_TIMESTAMP - INTERVAL '12 hours')
ON CONFLICT DO NOTHING;

-- Package Members: ARCHIVE (using HDE_MASTER as highest quality source)
INSERT INTO package_members (package_id, version_id, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440602', '550e8400-e29b-41d4-a716-446655440301', CURRENT_TIMESTAMP - INTERVAL '12 hours'),
    ('550e8400-e29b-41d4-a716-446655440602', '550e8400-e29b-41d4-a716-446655440302', CURRENT_TIMESTAMP - INTERVAL '12 hours')
ON CONFLICT DO NOTHING;

-- Events: ARCHIVED
INSERT INTO events (shot_id, event_type, package_id, actor, tool, created_at)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440602', 'Archive Operator', 'Archive Service', CURRENT_TIMESTAMP - INTERVAL '12 hours'),
    ('550e8400-e29b-41d4-a716-446655440002', 'ARCHIVED', '550e8400-e29b-41d4-a716-446655440602', 'Archive Operator', 'Archive Service', CURRENT_TIMESTAMP - INTERVAL '12 hours')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES (run manually after seed to confirm integrity)
-- ============================================================================

-- Expected counts:
-- SELECT 'productions' as table_name, COUNT(*) as count FROM productions;  -- Expected: 1
-- SELECT 'shots' as table_name, COUNT(*) as count FROM shots;  -- Expected: 5
-- SELECT 'assets' as table_name, COUNT(*) as count FROM assets;  -- Expected: 5
-- SELECT 'versions' as table_name, COUNT(*) as count FROM versions;  -- Expected: 18 (5 camera + 5 hde + 5 dailies + 3 edit)
-- SELECT 'version_lineage' as table_name, COUNT(*) as count FROM version_lineage;  -- Expected: 13
-- SELECT 'events' as table_name, COUNT(*) as count FROM events;  -- Expected: 18 (5 capture + 5 hde + 5 dailies + 3 edit + 3 turnover + 2 archive)
-- SELECT 'packages' as table_name, COUNT(*) as count FROM packages;  -- Expected: 2
-- SELECT 'package_members' as table_name, COUNT(*) as count FROM package_members;  -- Expected: 5 (3 turnover + 2 archive)

-- FK integrity checks (should return 0 rows if all FKs are valid):
-- SELECT 'assets with invalid shot_id' as check_name, COUNT(*) as violations FROM assets a LEFT JOIN shots s ON a.shot_id = s.id WHERE s.id IS NULL;
-- SELECT 'assets with invalid production_id' as check_name, COUNT(*) as violations FROM assets a LEFT JOIN productions p ON a.production_id = p.id WHERE p.id IS NULL;
-- SELECT 'shots with invalid production_id' as check_name, COUNT(*) as violations FROM shots s LEFT JOIN productions p ON s.production_id = p.id WHERE p.id IS NULL;
-- SELECT 'versions with invalid asset_id' as check_name, COUNT(*) as violations FROM versions v LEFT JOIN assets a ON v.asset_id = a.id WHERE a.id IS NULL;
-- SELECT 'versions with invalid derived_from_version_id' as check_name, COUNT(*) as violations FROM versions v LEFT JOIN versions v2 ON v.derived_from_version_id = v2.id WHERE v.derived_from_version_id IS NOT NULL AND v2.id IS NULL;
-- SELECT 'version_lineage with invalid derived_version_id' as check_name, COUNT(*) as violations FROM version_lineage vl LEFT JOIN versions v ON vl.derived_version_id = v.id WHERE v.id IS NULL;
-- SELECT 'version_lineage with invalid source_version_id' as check_name, COUNT(*) as violations FROM version_lineage vl LEFT JOIN versions v ON vl.source_version_id = v.id WHERE v.id IS NULL;
-- SELECT 'events with invalid shot_id' as check_name, COUNT(*) as violations FROM events e LEFT JOIN shots s ON e.shot_id = s.id WHERE s.id IS NULL;
-- SELECT 'events with invalid version_id' as check_name, COUNT(*) as violations FROM events e LEFT JOIN versions v ON e.version_id = v.id WHERE e.version_id IS NOT NULL AND v.id IS NULL;
-- SELECT 'events with invalid package_id' as check_name, COUNT(*) as violations FROM events e LEFT JOIN packages p ON e.package_id = p.id WHERE e.package_id IS NOT NULL AND p.id IS NULL;
-- SELECT 'packages with invalid production_id' as check_name, COUNT(*) as violations FROM packages p LEFT JOIN productions pr ON p.production_id = pr.id WHERE pr.id IS NULL;
-- SELECT 'package_members with invalid package_id' as check_name, COUNT(*) as violations FROM package_members pm LEFT JOIN packages p ON pm.package_id = p.id WHERE p.id IS NULL;
-- SELECT 'package_members with invalid version_id' as check_name, COUNT(*) as violations FROM package_members pm LEFT JOIN versions v ON pm.version_id = v.id WHERE v.id IS NULL;
