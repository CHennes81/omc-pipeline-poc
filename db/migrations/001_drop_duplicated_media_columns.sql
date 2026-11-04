-- Phase B: the OMC-JSON payload (versions.omc_json) is now the only home for these attributes.
-- Apply to a database created from the earlier schema.sql. Idempotent. Reseed afterwards
-- (POST /api/import/seed {"mode":"reset_and_seed"}) so omc_json carries the clip name (assetFC.functionalProperties.clipName).
-- Data in these columns is NOT copied anywhere by this script: reseed from db/seed.sql, whose payloads already
-- hold every value (verified equal to the old columns before they were dropped).
ALTER TABLE versions DROP COLUMN IF EXISTS codec;
ALTER TABLE versions DROP COLUMN IF EXISTS container;
ALTER TABLE versions DROP COLUMN IF EXISTS bitrate;
ALTER TABLE versions DROP COLUMN IF EXISTS fps;
ALTER TABLE versions DROP COLUMN IF EXISTS timecode_in;
ALTER TABLE versions DROP COLUMN IF EXISTS timecode_out;
ALTER TABLE assets DROP COLUMN IF EXISTS clip_name;
ALTER TABLE assets DROP COLUMN IF EXISTS reel_or_roll;
ALTER TABLE assets DROP COLUMN IF EXISTS camera_serial;
