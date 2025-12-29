-- Production Lineage Concierge POC - Database Schema
-- Phase 1: Deterministic lineage and auditability

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Productions
CREATE TABLE IF NOT EXISTS productions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Shots
CREATE TABLE IF NOT EXISTS shots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    production_id UUID NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    shot_code VARCHAR(50) NOT NULL,
    scene VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(production_id, shot_code)
);

-- Assets
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shot_id UUID NOT NULL REFERENCES shots(id) ON DELETE CASCADE,
    production_id UUID NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    asset_type VARCHAR(50) NOT NULL,
    clip_name VARCHAR(255),
    reel_or_roll VARCHAR(50),
    camera_serial VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Versions
CREATE TABLE IF NOT EXISTS versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    version_type VARCHAR(50) NOT NULL, -- CAMERA_ORIGINAL, HDE_MASTER, DAILIES_PROXY, EDIT_EXPORT, etc.
    derived_from_version_id UUID REFERENCES versions(id),
    storage_uri TEXT NOT NULL,
    codec VARCHAR(50),
    container VARCHAR(50),
    bitrate INTEGER,
    fps NUMERIC(10, 2),
    timecode_in VARCHAR(20),
    timecode_out VARCHAR(20),
    omc_json JSONB,
    creative_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Version Lineage (explicit edges for multi-input transforms in Phase 2)
CREATE TABLE IF NOT EXISTS version_lineage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    derived_version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
    source_version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
    transform_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(derived_version_id, source_version_id)
);

-- Packages
CREATE TABLE IF NOT EXISTS packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    production_id UUID NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    package_type VARCHAR(50) NOT NULL, -- TURNOVER, ARCHIVE, etc.
    label VARCHAR(255) NOT NULL,
    vendor VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Package Members
CREATE TABLE IF NOT EXISTS package_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    package_id UUID NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(package_id, version_id)
);

-- Events (immutable audit log)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shot_id UUID NOT NULL REFERENCES shots(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- CAPTURE, HDE_TRANSCODE, DAILIES_PUBLISHED, EDIT_EXPORT_CREATED, TURNOVER_DELIVERED, ARCHIVED
    version_id UUID REFERENCES versions(id),
    package_id UUID REFERENCES packages(id),
    actor VARCHAR(255), -- user or service name
    tool VARCHAR(255), -- service/tool that performed the action
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_shots_production_id ON shots(production_id);
CREATE INDEX IF NOT EXISTS idx_shots_shot_code ON shots(shot_code);
CREATE INDEX IF NOT EXISTS idx_assets_shot_id ON assets(shot_id);
CREATE INDEX IF NOT EXISTS idx_assets_production_id ON assets(production_id);
CREATE INDEX IF NOT EXISTS idx_versions_asset_id ON versions(asset_id);
CREATE INDEX IF NOT EXISTS idx_versions_version_type ON versions(version_type);
CREATE INDEX IF NOT EXISTS idx_versions_derived_from ON versions(derived_from_version_id);
CREATE INDEX IF NOT EXISTS idx_version_lineage_derived ON version_lineage(derived_version_id);
CREATE INDEX IF NOT EXISTS idx_version_lineage_source ON version_lineage(source_version_id);
CREATE INDEX IF NOT EXISTS idx_packages_production_id ON packages(production_id);
CREATE INDEX IF NOT EXISTS idx_package_members_package_id ON package_members(package_id);
CREATE INDEX IF NOT EXISTS idx_package_members_version_id ON package_members(version_id);
CREATE INDEX IF NOT EXISTS idx_events_shot_id ON events(shot_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);

-- JSONB indexes for common OMC queries
CREATE INDEX IF NOT EXISTS idx_versions_omc_json ON versions USING GIN(omc_json);
CREATE INDEX IF NOT EXISTS idx_events_details ON events USING GIN(details);

