import { formatDateTime, isUUID, normalizeTimecode } from '../utils/formatting';
import './VersionAuditCard.css';

interface VersionAuditCardProps {
  version: Record<string, unknown>;
}

/**
 * Format version_type by removing underscores and converting to Title Case
 * Example: "CAMERA_ORIGINAL" -> "Camera Original"
 */
function formatVersionType(versionType: unknown): string {
  if (!versionType) return '—';
  return String(versionType)
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export function VersionAuditCard({ version }: VersionAuditCardProps) {
  // Extract fields with multiple possible key formats
  const versionType = version['version_type'] || version['Version Type'] || version['Version_type'];
  const createdAt = version['created_at'] || version['Created At'] || version['Created_at'];
  const codec = version['codec'] || version['Codec'];
  const fps = version['fps'] || version['Fps'] || version['FPS'];
  const timecodeIn = version['timecode_in'] || version['Timecode In'] || version['Timecode_in'];
  const timecodeOut = version['timecode_out'] || version['Timecode Out'] || version['Timecode_out'];
  const reel = version['reel'] || version['Reel'];
  const storageUri =
    version['storage_uri'] ||
    version['Storage URI'] ||
    version['Storage_uri'] ||
    version['storageURI'];
  const versionId = Object.entries(version).find(([, val]) => isUUID(val))?.[1] as
    | string
    | undefined;

  // Format values, using "—" for missing/null/empty
  const formatValue = (val: unknown): string => {
    if (val === null || val === undefined || val === '') return '—';
    return String(val);
  };

  const formatTimecode = (val: unknown): string => {
    if (val === null || val === undefined || val === '') return '—';
    return normalizeTimecode(String(val));
  };

  return (
    <div className="version-audit-card">
      {/* Line 1: Version Type (left) and Created (right) */}
      <div className="version-audit-line1">
        <span className="version-audit-field">
          <span className="version-audit-label">Version Type:</span>
          <span className="version-audit-value">{formatVersionType(versionType)}</span>
        </span>
        <span className="version-audit-field" style={{ marginLeft: 'auto' }}>
          <span className="version-audit-label">Created:</span>
          <span className="version-audit-value">
            {createdAt ? formatDateTime(String(createdAt)) : '—'}
          </span>
        </span>
      </div>

      {/* Line 2: Codec, FPS, Timecode In, Timecode Out (all always shown) */}
      <div className="version-audit-line2">
        <span className="version-audit-field">
          <span className="version-audit-label">Codec:</span>
          <span className="version-audit-value">{formatValue(codec)}</span>
        </span>
        <span className="version-audit-field">
          <span className="version-audit-label">FPS:</span>
          <span className="version-audit-value">{formatValue(fps)}</span>
        </span>
        <span className="version-audit-field">
          <span className="version-audit-label">Timecode In:</span>
          <span className="version-audit-value">{formatTimecode(timecodeIn)}</span>
        </span>
        <span className="version-audit-field">
          <span className="version-audit-label">Timecode Out:</span>
          <span className="version-audit-value">{formatTimecode(timecodeOut)}</span>
        </span>
      </div>

      {/* Line 3: Reel (left) and Version ID (right - de-emphasized grey) */}
      <div className="version-audit-line3">
        <span className="version-audit-field">
          <span className="version-audit-label">Reel:</span>
          <span className="version-audit-value">{formatValue(reel)}</span>
        </span>
        <span className="version-audit-field version-audit-version-id-field">
          <span className="version-audit-label">Version ID:</span>
          <span className="version-audit-uuid">{versionId || '—'}</span>
        </span>
      </div>

      {/* Divider and Storage URI */}
      <div className="version-audit-uri-section">
        <span className="version-audit-label">Storage URI:</span>
        <span className="version-audit-uri">{formatValue(storageUri)}</span>
      </div>
    </div>
  );
}
