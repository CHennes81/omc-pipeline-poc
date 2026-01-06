/**
 * Format a date string to "D MMM YYYY @ HH:mm" format (local time, no seconds, no timezone)
 * Example: "28 Dec 2025 @ 22:06"
 */
export function formatDateTime(dateString: string | null | undefined): string {
  if (!dateString) return '-';
  try {
    const date = new Date(dateString);
    const day = date.getDate().toString();
    const monthNames = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    const month = monthNames[date.getMonth()];
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${day} ${month} ${year} @ ${hours}:${minutes}`;
  } catch {
    return String(dateString);
  }
}

/**
 * Format a label by removing underscores and capitalizing words
 */
export function formatLabel(key: string): string {
  return key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Format Answer string to insert line break before URI
 * Looks for patterns like "text: dam://..." or "text: http://..." or "text: file://..."
 */
export function formatAnswer(answer: string): string {
  // Match colon followed by optional whitespace and a URI scheme (dam://, http://, https://, file://, etc.)
  return answer.replace(/: (\s*)([a-zA-Z][a-zA-Z0-9+.-]*:\/\/)/g, ':\n$2');
}

/**
 * Check if a string looks like a UUID
 */
export function isUUID(value: unknown): boolean {
  if (typeof value !== 'string') return false;
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(value);
}

/**
 * Check if a string looks like a shot code
 */
export function isShotCode(value: unknown): boolean {
  if (typeof value !== 'string') return false;
  // Shot codes typically look like "011_021" or similar patterns
  return /^\d{3}_\d{3}$/.test(value);
}

/**
 * Normalize timecode to HH:MM:SS.SSS format
 * Handles formats like:
 * - 01:00:10:00 (SMPTE with frames)
 * - 01:00:10.000 (already correct)
 * - 01:00:10 (missing milliseconds)
 */
export function normalizeTimecode(timecode: string | null | undefined): string {
  if (!timecode) return '-';
  const str = String(timecode).trim();

  // If already in HH:MM:SS.SSS format, return as is
  if (/^\d{2}:\d{2}:\d{2}\.\d{3}$/.test(str)) {
    return str;
  }

  // Handle SMPTE format HH:MM:SS:FF (frames)
  const smpteMatch = str.match(/^(\d{2}):(\d{2}):(\d{2}):(\d{2})$/);
  if (smpteMatch) {
    const [, hours, minutes, seconds] = smpteMatch;
    // Set to .000 since we don't know the frame rate to convert frames to milliseconds
    return `${hours}:${minutes}:${seconds}.000`;
  }

  // Handle HH:MM:SS (missing milliseconds)
  const basicMatch = str.match(/^(\d{2}):(\d{2}):(\d{2})$/);
  if (basicMatch) {
    const [, hours, minutes, seconds] = basicMatch;
    return `${hours}:${minutes}:${seconds}.000`;
  }

  // If we can't parse it, return as is
  return str;
}
