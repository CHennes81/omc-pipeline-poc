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
 * Helper function to normalize stage value for display.
 * Converts "DAILIES" -> "Dailies", "EDIT_EXPORT" -> "Edit Export", etc.
 */
function normalizeStage(stage: string): string {
  if (!stage || stage.trim() === '' || stage === '-') {
    return stage;
  }

  const trimmed = stage.trim();

  // If already human-readable (has spaces or mixed case), return as-is
  if (
    trimmed.includes(' ') ||
    (trimmed !== trimmed.toUpperCase() && trimmed !== trimmed.toLowerCase())
  ) {
    return trimmed;
  }

  // Convert SNAKE_CASE or UPPERCASE to Title Case
  return trimmed
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

// Temporary flag to log shot structure once for debugging
let hasLoggedShot = false;

/**
 * Helper function to extract stage from multiple possible field names.
 * Checks various possible keys including nested structures.
 * Returns normalized stage string or null if not found.
 */
function extractStage(shot: ShotAuditItem): string | null {
  // Temporary logging in dev mode to inspect shot structure (remove after verification)
  if (import.meta.env.DEV && !hasLoggedShot) {
    console.log('ShotsAuditCard shot:', shot);
    hasLoggedShot = true;
  }

  // Try direct keys first
  let stage: string | null = null;

  // Check common direct keys
  const directKeys = [
    'stage',
    'Stage',
    'STAGE',
    'pipeline_stage',
    'Pipeline_Stage',
    'PIPELINE_STAGE',
    'shot_stage',
    'Shot_Stage',
    'SHOT_STAGE',
    'current_stage',
    'Current_Stage',
    'CURRENT_STAGE',
    'stage_name',
    'Stage_Name',
    'STAGE_NAME',
    'stageName',
    'workflow_stage',
    'Workflow_Stage',
    'WORKFLOW_STAGE',
    'workflowStage',
    'status',
    'Status',
    'STATUS',
    'state',
    'State',
    'STATE',
  ];

  for (const key of directKeys) {
    const value = shot[key];
    if (value && typeof value === 'string' && value.trim() && value !== '-') {
      stage = value.trim();
      break;
    }
  }

  // Check nested structures (e.g., shot.stage.name, shot.stage.stage_name)
  if (!stage && typeof shot.stage === 'object' && shot.stage !== null) {
    const stageObj = shot.stage as Record<string, unknown>;
    const nestedKeys = ['name', 'stage_name', 'stageName', 'value', 'label'];
    for (const key of nestedKeys) {
      const value = stageObj[key];
      if (value && typeof value === 'string' && value.trim() && value !== '-') {
        stage = value.trim();
        break;
      }
    }
  }

  return stage ? normalizeStage(stage) : null;
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
            <span className="shot-audit-field shot-audit-stage-field">
              <span className="shot-audit-label">Stage:</span>
              <span className="shot-audit-value">{stage || '—'}</span>
            </span>
          </div>
        );
      })}
    </div>
  );
}
