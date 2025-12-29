-- Production Lineage Concierge POC - Database Views
-- Phase 1: Deterministic stage computation

-- View: Current lifecycle stage per shot
-- Stage is derived from most advanced completed event per shot
CREATE OR REPLACE VIEW v_shot_stage AS
WITH shot_events AS (
    SELECT DISTINCT ON (shot_id)
        shot_id,
        event_type,
        created_at
    FROM events
    ORDER BY shot_id,
             CASE event_type
                 WHEN 'ARCHIVED' THEN 6
                 WHEN 'TURNOVER_DELIVERED' THEN 5
                 WHEN 'EDIT_EXPORT_CREATED' THEN 4
                 WHEN 'DAILIES_PUBLISHED' THEN 3
                 WHEN 'HDE_TRANSCODE' THEN 2
                 WHEN 'OFFLOAD' THEN 2
                 WHEN 'CAPTURE' THEN 1
                 ELSE 0
             END DESC,
             created_at DESC
)
SELECT
    s.id AS shot_id,
    s.production_id,
    s.shot_code,
    s.scene,
    s.description,
    COALESCE(
        CASE se.event_type
            WHEN 'ARCHIVED' THEN 'ARCHIVE'
            WHEN 'TURNOVER_DELIVERED' THEN 'TURNOVER'
            WHEN 'EDIT_EXPORT_CREATED' THEN 'EDIT_EXPORT'
            WHEN 'DAILIES_PUBLISHED' THEN 'DAILIES'
            WHEN 'HDE_TRANSCODE' THEN 'OFFLOAD'
            WHEN 'OFFLOAD' THEN 'OFFLOAD'
            WHEN 'CAPTURE' THEN 'CAPTURE'
            ELSE 'NEW'
        END,
        'NEW'
    ) AS stage,
    se.event_type AS last_event_type,
    se.created_at AS last_event_at
FROM shots s
LEFT JOIN shot_events se ON s.id = se.shot_id;

