-- Seed Data Verification Queries
-- Run these after loading seed.sql to confirm referential integrity

-- Expected counts
SELECT 'productions' as table_name, COUNT(*) as count FROM productions;
SELECT 'shots' as table_name, COUNT(*) as count FROM shots;
SELECT 'assets' as table_name, COUNT(*) as count FROM assets;
SELECT 'versions' as table_name, COUNT(*) as count FROM versions;
SELECT 'version_lineage' as table_name, COUNT(*) as count FROM version_lineage;
SELECT 'events' as table_name, COUNT(*) as count FROM events;
SELECT 'packages' as table_name, COUNT(*) as count FROM packages;
SELECT 'package_members' as table_name, COUNT(*) as count FROM package_members;

-- FK integrity checks (should return 0 violations if all FKs are valid)
SELECT 'assets with invalid shot_id' as check_name, COUNT(*) as violations
FROM assets a LEFT JOIN shots s ON a.shot_id = s.id WHERE s.id IS NULL;

SELECT 'assets with invalid production_id' as check_name, COUNT(*) as violations
FROM assets a LEFT JOIN productions p ON a.production_id = p.id WHERE p.id IS NULL;

SELECT 'shots with invalid production_id' as check_name, COUNT(*) as violations
FROM shots s LEFT JOIN productions p ON s.production_id = p.id WHERE p.id IS NULL;

SELECT 'versions with invalid asset_id' as check_name, COUNT(*) as violations
FROM versions v LEFT JOIN assets a ON v.asset_id = a.id WHERE a.id IS NULL;

SELECT 'versions with invalid derived_from_version_id' as check_name, COUNT(*) as violations
FROM versions v LEFT JOIN versions v2 ON v.derived_from_version_id = v2.id
WHERE v.derived_from_version_id IS NOT NULL AND v2.id IS NULL;

SELECT 'version_lineage with invalid derived_version_id' as check_name, COUNT(*) as violations
FROM version_lineage vl LEFT JOIN versions v ON vl.derived_version_id = v.id WHERE v.id IS NULL;

SELECT 'version_lineage with invalid source_version_id' as check_name, COUNT(*) as violations
FROM version_lineage vl LEFT JOIN versions v ON vl.source_version_id = v.id WHERE v.id IS NULL;

SELECT 'events with invalid shot_id' as check_name, COUNT(*) as violations
FROM events e LEFT JOIN shots s ON e.shot_id = s.id WHERE s.id IS NULL;

SELECT 'events with invalid version_id' as check_name, COUNT(*) as violations
FROM events e LEFT JOIN versions v ON e.version_id = v.id
WHERE e.version_id IS NOT NULL AND v.id IS NULL;

SELECT 'events with invalid package_id' as check_name, COUNT(*) as violations
FROM events e LEFT JOIN packages p ON e.package_id = p.id
WHERE e.package_id IS NOT NULL AND p.id IS NULL;

SELECT 'packages with invalid production_id' as check_name, COUNT(*) as violations
FROM packages p LEFT JOIN productions pr ON p.production_id = pr.id WHERE pr.id IS NULL;

SELECT 'package_members with invalid package_id' as check_name, COUNT(*) as violations
FROM package_members pm LEFT JOIN packages p ON pm.package_id = p.id WHERE p.id IS NULL;

SELECT 'package_members with invalid version_id' as check_name, COUNT(*) as violations
FROM package_members pm LEFT JOIN versions v ON pm.version_id = v.id WHERE v.id IS NULL;
