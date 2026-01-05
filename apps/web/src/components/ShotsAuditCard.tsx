import { Link } from 'react-router-dom';
import './ShotsAuditCard.css';

interface ShotAuditItem {
  shot_code?: string;
  shotCode?: string;
  description?: string | null;
  stage?: string;
  scene?: string | null;
  [key: string]: unknown;
}

interface ShotsAuditCardProps {
  shots: ShotAuditItem[];
}

/**
 * Helper function to extract stage from multiple possible field names.
 * Returns the first available value, or null if none found.
 */
function extractStage(shot: ShotAuditItem): string | null {
  const stage =
    shot.stage ||
    shot.Stage ||
    shot.pipeline_stage ||
    shot.Pipeline_Stage ||
    shot.shot_stage ||
    shot.Shot_Stage ||
    shot.current_stage ||
    shot.Current_Stage ||
    shot.status ||
    shot.Status ||
    null;
  return stage && stage !== '-' ? String(stage) : null;
}

/**
 * Renders shots in audit format, matching VersionAuditCard pattern.
 * Each shot renders on ONE LINE:
 * - Description: <desc>    Shot Code: <clickable_code>    Scene: <scene>    Stage: <pill_or_text>
 * - Stage is always shown (rightmost)
 */
export function ShotsAuditCard({ shots }: ShotsAuditCardProps) {
  if (shots.length === 0) {
    return <p className="page-empty">No shots found</p>;
  }

  return (
    <div className="shots-audit-card">
      {shots.map((shot, idx) => {
        const shotCode = shot.shot_code || shot.shotCode;
        const description = shot.description || null;
        const scene = shot.scene || null;
        const stage = extractStage(shot);

        return (
          <div key={shotCode || idx} className="shot-audit-item">
            <div className="shot-audit-content">
              <span className="shot-audit-field">
                <span className="shot-audit-label">Description:</span>
                <span className="shot-audit-value" title={description || undefined}>
                  {description || '—'}
                </span>
              </span>
              <span className="shot-audit-field">
                <span className="shot-audit-label">Shot Code:</span>
                {shotCode ? (
                  <Link to={`/shot/${shotCode}`} className="shot-audit-code">
                    {shotCode}
                  </Link>
                ) : (
                  <span className="shot-audit-value">—</span>
                )}
              </span>
              <span className="shot-audit-field">
                <span className="shot-audit-label">Scene:</span>
                <span className="shot-audit-value">{scene || '—'}</span>
              </span>
            </div>
            <span className="shot-audit-field shot-audit-stage-field">
              <span className="shot-audit-label">Stage:</span>
              {stage ? (
                <span className="stage-badge" data-stage={stage}>
                  {stage.replace(/_/g, ' ')}
                </span>
              ) : (
                <span className="shot-audit-value">—</span>
              )}
            </span>
          </div>
        );
      })}
    </div>
  );
}
