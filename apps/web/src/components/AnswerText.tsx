import { Link } from 'react-router-dom';
import { isShotCode } from '../utils/formatting';

interface AnswerTextProps {
  text: string;
}

/**
 * Renders answer text with only shot codes as links.
 * URIs and other text remain plain text.
 * Shot codes inside URIs are not linked.
 */
export function AnswerText({ text }: AnswerTextProps) {
  // URI patterns to exclude from linking (dam://, http://, https://, file://, etc.)
  const uriPattern = /[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^\s]*/g;
  const uriMatches: Array<{ start: number; end: number }> = [];
  let uriMatch;

  // Find all URIs in the text
  while ((uriMatch = uriPattern.exec(text)) !== null) {
    uriMatches.push({ start: uriMatch.index, end: uriMatch.index + uriMatch[0].length });
  }

  // Check if a position is inside a URI
  const isInsideUri = (pos: number): boolean => {
    return uriMatches.some((uri) => pos >= uri.start && pos < uri.end);
  };

  // Split text by shot codes and render appropriately
  // Shot codes match pattern: \d{3}_\d{3}
  const shotCodeRegex = /(\d{3}_\d{3})/g;
  const parts: Array<{ text: string; isShotCode: boolean }> = [];
  let lastIndex = 0;
  let match;

  while ((match = shotCodeRegex.exec(text)) !== null) {
    // Add text before the shot code
    if (match.index > lastIndex) {
      parts.push({ text: text.substring(lastIndex, match.index), isShotCode: false });
    }
    // Add the shot code - only link if it's not inside a URI
    if (isShotCode(match[1]) && !isInsideUri(match.index)) {
      parts.push({ text: match[1], isShotCode: true });
    } else {
      parts.push({ text: match[1], isShotCode: false });
    }
    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push({ text: text.substring(lastIndex), isShotCode: false });
  }

  // If no shot codes found, return plain text
  if (parts.length === 0) {
    return <span>{text}</span>;
  }

  // Process text to add line breaks before URIs (dam://, http://, etc.)
  const processedParts = parts.map((part) => {
    if (part.isShotCode) {
      return part;
    }
    // Add line break before URI patterns (colon followed by URI scheme)
    const textWithBreaks = part.text.replace(/: (\s*)([a-zA-Z][a-zA-Z0-9+.-]*:\/\/)/g, ':\n$2');
    return { ...part, text: textWithBreaks };
  });

  return (
    <span style={{ whiteSpace: 'pre-wrap' }}>
      {processedParts.map((part, idx) => {
        if (part.isShotCode) {
          return (
            <Link key={idx} to={`/shot/${part.text}`} className="page-link">
              {part.text}
            </Link>
          );
        }
        return <span key={idx}>{part.text}</span>;
      })}
    </span>
  );
}
