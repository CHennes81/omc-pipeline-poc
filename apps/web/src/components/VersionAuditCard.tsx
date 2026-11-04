import { useLayoutEffect, useRef, useState, type ReactNode } from 'react';
import { formatDateTime, isUUID, normalizeTimecode } from '../utils/formatting';
import './VersionAuditCard.css';

interface VersionAuditCardProps {
  version: Record<string, unknown>;
}

type Version = Record<string, unknown>;

interface DeliveredIn {
  package_type?: string | null;
  label?: string | null;
  vendor?: string | null;
}

/** Minimum whitespace (px) between the end of the locator and the Version ID when they share a line. */
const LOCATOR_MIN_GAP = 24;
/** Must equal `column-gap` on .version-audit-locator-row in the CSS (the hidden measurer mirrors the row). */
const LOCATOR_ROW_GAP = 8;

/** Shown when a value is legitimately absent (e.g. no Reason on a first export, nothing delivered yet). */
const NA = '(n/a)';

/** "CAMERA_ORIGINAL" -> "Camera Original" */
function titleCase(value: unknown): string {
  if (!value) return NA;
  return String(value)
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/** First present value among the given keys, as a trimmed string (null when empty). */
function pick(version: Version, ...keys: string[]): string | null {
  for (const key of keys) {
    const raw = version[key];
    if (raw !== null && raw !== undefined && String(raw).trim() !== '') return String(raw).trim();
  }
  return null;
}

/** Join the parts that exist; "(n/a)" when none do. */
function joinParts(parts: Array<string | null | undefined>, separator = ' · '): string {
  const present = parts.filter((p): p is string => !!p && p.trim() !== '');
  return present.length > 0 ? present.join(separator) : NA;
}

function timecode(value: string | null): string {
  return value ? normalizeTimecode(value) : NA;
}

function formatLine(v: Version): string {
  const width = pick(v, 'width');
  const height = pick(v, 'height');
  const fps = pick(v, 'fps', 'Fps', 'FPS');
  return joinParts([
    pick(v, 'codec', 'Codec'),
    pick(v, 'container'),
    width && height ? `${width}×${height}` : null,
    fps ? `${fps} fps` : null,
    pick(v, 'color_space'),
  ]);
}

function cameraLine(v: Version): string {
  const ei = pick(v, 'exposure_index');
  return joinParts([
    joinParts([pick(v, 'camera_make'), pick(v, 'camera_model')], ' '),
    pick(v, 'camera_serial'),
    ei ? `EI ${ei}` : null,
  ]);
}

function lensLine(v: Version): string {
  const focal = pick(v, 'focal_length');
  const tStop = pick(v, 't_stop');
  return joinParts([
    joinParts([pick(v, 'lens_make'), pick(v, 'lens_model')], ' '),
    focal ? `${focal} mm` : null,
    tStop ? `T${tStop}` : null,
  ]);
}

function sourceLine(v: Version): string {
  const reel = pick(v, 'source_reel');
  const clip = pick(v, 'source_clip_name');
  return joinParts([reel ? `Reel ${reel}` : null, clip ? `Clip ${clip}` : null]);
}

function deliveredInLine(v: Version): string {
  const list = Array.isArray(v['delivered_in']) ? (v['delivered_in'] as DeliveredIn[]) : [];
  return joinParts(
    list.map((p) => {
      const type = titleCase(p.package_type);
      return p.vendor ? `${type} (${p.vendor})` : type;
    }),
  );
}

/** Created By: the actor, plus the tool when it adds information. */
function createdByLine(v: Version, includeTool: boolean): string {
  return joinParts([pick(v, 'created_by_actor'), includeTool ? pick(v, 'created_by_tool') : null]);
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <>
      <span className="version-audit-label">{label}:</span>
      <span className="version-audit-row-value">{children}</span>
    </>
  );
}

function InlinePair({ label, value }: { label: string; value: string }) {
  return (
    <span className="version-audit-inline-pair">
      <span className="version-audit-label">{label}:</span>
      <span>{value}</span>
    </span>
  );
}

/**
 * Locator on one line with the Version ID right-justified when "Locator: <uri>   Version ID: <id>" fits with at
 * least LOCATOR_MIN_GAP of whitespace; otherwise the URI drops to its own line under the label and the label and
 * Version ID share the first line. Measured from a hidden single-line copy, so it follows the card width.
 */
function LocatorRow({ uri, versionId }: { uri: string | null; versionId: string | null }) {
  const rowRef = useRef<HTMLDivElement>(null);
  const measureRef = useRef<HTMLDivElement>(null);
  const [stacked, setStacked] = useState(false);

  useLayoutEffect(() => {
    const row = rowRef.current;
    const measure = measureRef.current;
    if (!row || !measure) return;
    const check = () => setStacked(measure.offsetWidth > row.clientWidth);
    check();
    const observer = new ResizeObserver(check);
    observer.observe(row);
    return () => observer.disconnect();
  }, [uri, versionId]);

  const uriText = uri ?? NA;
  const idText = versionId ?? NA;

  return (
    <div className="version-audit-locator-section">
      <div
        ref={rowRef}
        className={`version-audit-locator-row${stacked ? ' version-audit-locator-stacked' : ''}`}
      >
        <span className="version-audit-label version-audit-locator-label">Locator:</span>
        <span className="version-audit-uri version-audit-locator-uri">{uriText}</span>
        <span className="version-audit-locator-id">
          <span className="version-audit-label">Version ID:</span>
          <span className="version-audit-uuid">{idText}</span>
        </span>
      </div>
      {/* Hidden single-line copy used only to measure the width the one-line layout needs. */}
      <div ref={measureRef} className="version-audit-locator-measure" aria-hidden="true">
        <span className="version-audit-label">Locator:</span>
        <span className="version-audit-uri">{uriText}</span>
        <span
          className="version-audit-locator-id"
          style={{ marginLeft: LOCATOR_MIN_GAP - LOCATOR_ROW_GAP }}
        >
          <span className="version-audit-label">Version ID:</span>
          <span className="version-audit-uuid">{idText}</span>
        </span>
      </div>
    </div>
  );
}

/**
 * Audit card for one version. The layout depends on the version type but always follows one pattern:
 * Version Type on top, the most significant information next, who made it last, then a separator and the Locator.
 *   CAMERA_ORIGINAL:           Camera, Format, Lens, Reel + Timecode, Captured By
 *   CAMERA_MASTER, DAILIES_PROXY (derived media): Format, Source, Timecode, Created By
 *   EDIT_EXPORT:               Format, Timecode, Reason, Delivered in, Created By
 * "(n/a)" means "this record has no value"; fields a type cannot carry are not shown.
 */
export function VersionAuditCard({ version }: VersionAuditCardProps) {
  const versionType = pick(version, 'version_type', 'Version Type', 'Version_type');
  const createdAt = pick(version, 'created_at', 'Created At', 'Created_at');
  const storageUri = pick(version, 'storage_uri', 'Storage URI', 'Storage_uri', 'storageURI');
  const tcIn = timecode(pick(version, 'timecode_in', 'Timecode In', 'Timecode_in'));
  const tcOut = timecode(pick(version, 'timecode_out', 'Timecode Out', 'Timecode_out'));
  const idValue = version['id'];
  const versionId =
    (isUUID(idValue) ? String(idValue) : undefined) ??
    (Object.values(version).find((val) => isUUID(val)) as string | undefined) ??
    null;

  let rows: ReactNode;
  if (versionType === 'CAMERA_ORIGINAL') {
    rows = (
      <>
        <Row label="Camera">{cameraLine(version)}</Row>
        <Row label="Format">{formatLine(version)}</Row>
        <Row label="Lens">{lensLine(version)}</Row>
        <Row label="Reel">
          <span>{pick(version, 'reel', 'Reel') ?? NA}</span>
          <InlinePair label="Timecode In" value={tcIn} />
          <InlinePair label="Timecode Out" value={tcOut} />
        </Row>
        <Row label="Captured By">{createdByLine(version, false)}</Row>
      </>
    );
  } else if (versionType === 'EDIT_EXPORT') {
    rows = (
      <>
        <Row label="Format">{formatLine(version)}</Row>
        <Row label="Timecode In">
          <span>{tcIn}</span>
          <InlinePair label="Timecode Out" value={tcOut} />
        </Row>
        <Row label="Reason">{pick(version, 'reason') ?? NA}</Row>
        <Row label="Delivered in">{deliveredInLine(version)}</Row>
        <Row label="Created By">{createdByLine(version, true)}</Row>
      </>
    );
  } else {
    // Derived media: CAMERA_MASTER, DAILIES_PROXY (and any type without its own layout)
    rows = (
      <>
        <Row label="Format">{formatLine(version)}</Row>
        <Row label="Source">{sourceLine(version)}</Row>
        <Row label="Timecode In">
          <span>{tcIn}</span>
          <InlinePair label="Timecode Out" value={tcOut} />
        </Row>
        <Row label="Created By">{createdByLine(version, true)}</Row>
      </>
    );
  }

  return (
    <div className="version-audit-card">
      <div className="version-audit-line1">
        <span className="version-audit-field">
          <span className="version-audit-label">Version Type:</span>
          <span className="version-audit-value">{titleCase(versionType)}</span>
        </span>
        <span className="version-audit-field" style={{ marginLeft: 'auto' }}>
          <span className="version-audit-label">Created:</span>
          <span className="version-audit-value">{createdAt ? formatDateTime(createdAt) : NA}</span>
        </span>
      </div>

      <div className="version-audit-rows">{rows}</div>

      <LocatorRow uri={storageUri} versionId={versionId} />
    </div>
  );
}
