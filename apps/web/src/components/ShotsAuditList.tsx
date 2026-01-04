import { Link } from 'react-router-dom';
import './ShotsAuditList.css';

interface ShotAuditItem {
  shot_code?: string;
  shotCode?: string;
  description?: string | null;
  stage?: string;
  scene?: string | null;
  [key: string]: unknown;
}

interface ShotsAuditListProps {
  shots: ShotAuditItem[];
}

/**
 * Renders a list of shots matching the All Shots page format:
 * - Description first (left)
 * - Shot Code as a link to Shot Detail (right of description)
 * - Stage at far right as a pill if it fits, else plain text
 */
export function ShotsAuditList({ shots }: ShotsAuditListProps) {
  if (shots.length === 0) {
    return <p className="page-empty">No shots found</p>;
  }

  return (
    <div className="shots-audit-list">
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Description</th>
              <th>Shot Code</th>
              <th>Scene</th>
              <th>Stage</th>
            </tr>
          </thead>
          <tbody>
            {shots.map((shot, idx) => {
              const shotCode = shot.shot_code || shot.shotCode;
              const description = shot.description || '-';
              const scene = shot.scene || '-';
              // Check multiple possible field names for stage
              const stage =
                shot.stage ||
                shot.Stage ||
                shot.pipeline_stage ||
                shot.Pipeline_Stage ||
                shot.shot_stage ||
                shot.Shot_Stage ||
                shot.status ||
                shot.Status ||
                '-';

              return (
                <tr key={shotCode || idx}>
                  <td>{description}</td>
                  <td>
                    {shotCode ? (
                      <Link
                        to={`/shot/${shotCode}`}
                        style={{ color: 'var(--dashboard-accent)', textDecoration: 'none' }}
                      >
                        {shotCode}
                      </Link>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>{scene}</td>
                  <td>
                    {stage && stage !== '-' ? (
                      <span className="stage-badge" data-stage={stage}>
                        {stage.replace(/_/g, ' ')}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
