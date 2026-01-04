import { formatDateTime, formatLabel, isUUID, normalizeTimecode } from '../utils/formatting';
import './VersionAuditCard.css';

interface VersionAuditCardProps {
  version: Record<string, unknown>;
}

export function VersionAuditCard({ version }: VersionAuditCardProps) {
  // Extract fields with multiple possible key formats
  const versionType = version['version_type'] || version['Version Type'] || version['Version_type'];
  const createdAt = version['created_at'] || version['Created At'] || version['Created_at'];
  const codec = version['codec'] || version['Codec'];
  const fps = version['fps'] || version['Fps'] || version['FPS'];
  const timecodeIn = version['timecode_in'] || version['Timecode In'] || version['Timecode_in'];
  const timecodeOut = version['timecode_out'] || version['Timecode Out'] || version['Timecode_out'];
  const storageUri =
    version['storage_uri'] ||
    version['Storage URI'] ||
    version['Storage_uri'] ||
    version['storageURI'];
  const versionId = Object.entries(version).find(([, val]) => isUUID(val))?.[1] as
    | string
    | undefined;

  // Build detail fields array (only Codec, Fps, Timecode In, Timecode Out if present)
  const detailFields: Array<[string, unknown]> = [];
  if (codec !== null && codec !== undefined && codec !== '') {
    detailFields.push(['codec', codec]);
  }
  if (fps !== null && fps !== undefined && fps !== '') {
    detailFields.push(['fps', fps]);
  }
  if (timecodeIn !== null && timecodeIn !== undefined && timecodeIn !== '') {
    detailFields.push(['timecode_in', normalizeTimecode(String(timecodeIn))]);
  }
  if (timecodeOut !== null && timecodeOut !== undefined && timecodeOut !== '') {
    detailFields.push(['timecode_out', normalizeTimecode(String(timecodeOut))]);
  }

  return (
    <div className="version-audit-card">
      {/* Line 1: Version Type and Created */}
      <div className="version-audit-line1">
        {versionType && (
          <span className="version-audit-field">
            <span className="version-audit-label">Version Type:</span>
            <span className="version-audit-value">{String(versionType)}</span>
          </span>
        )}
        {createdAt && (
          <span className="version-audit-field">
            <span className="version-audit-label">Created:</span>
            <span className="version-audit-value">{formatDateTime(String(createdAt))}</span>
          </span>
        )}
      </div>

      {/* Line 2: Details (Codec, FPS, Timecode In, Timecode Out) */}
      {detailFields.length > 0 && (
        <div className="version-audit-line2">
          {detailFields.map(([key, val]) => (
            <span key={key} className="version-audit-field">
              <span className="version-audit-label">{formatLabel(key)}:</span>
              <span className="version-audit-value">{String(val)}</span>
            </span>
          ))}
        </div>
      )}

      {/* Line 3: Version ID (before divider) */}
      {versionId && (
        <div className="version-audit-line3">
          <span className="version-audit-label">Version ID:</span>
          <span className="version-audit-uuid">{versionId}</span>
        </div>
      )}

      {/* Divider and Storage URI */}
      {storageUri && (
        <div className="version-audit-uri-section">
          <span className="version-audit-label">Storage URI:</span>
          <span className="version-audit-uri">{String(storageUri)}</span>
        </div>
      )}
    </div>
  );
}
