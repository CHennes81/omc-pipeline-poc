import { useState } from 'react';

export interface AskError {
  httpStatus: number;
  url: string;
  code: string;
  message: string;
  rawBody?: string;
  timestamp: string;
}

interface AskErrorPanelProps {
  error: AskError;
}

/**
 * AskErrorPanel displays user-friendly error messages for Ask failures.
 * Shows exactly two user messages per Appendix E:
 * - Unanswerable question
 * - Data retrieval failure
 * In dev mode only, shows collapsible diagnostic details.
 */
export function AskErrorPanel({ error }: AskErrorPanelProps) {
  const [showDetails, setShowDetails] = useState(false);
  const isDev = import.meta.env.DEV;

  // Map error codes to user message types per Appendix E
  const isUnanswerable =
    error.code === 'unsupported_question' || error.code === 'ambiguous_question';

  const userMessage = isUnanswerable
    ? {
        title: "This question can't be answered",
        body: "The system couldn't map your question to a supported, verifiable query.\nPlease select one of the supported questions or rephrase your request.",
      }
    : {
        title: 'Unable to retrieve data',
        body: 'The system encountered an internal error while answering this question.\nPlease contact your system administrator for assistance.',
      };

  return (
    <div className="page-error" style={{ marginBottom: '24px' }}>
      <div style={{ marginBottom: '12px' }}>
        <strong style={{ fontSize: '16px', display: 'block', marginBottom: '8px' }}>
          {userMessage.title}
        </strong>
        <div style={{ whiteSpace: 'pre-wrap', color: 'var(--dashboard-text-secondary)' }}>
          {userMessage.body}
        </div>
      </div>

      {isDev && (
        <div
          style={{
            marginTop: '16px',
            borderTop: '1px solid var(--dashboard-border)',
            paddingTop: '12px',
          }}
        >
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="page-button-link"
            style={{ fontSize: '13px', marginBottom: showDetails ? '12px' : 0 }}
          >
            {showDetails ? 'Hide' : 'Show'} Error Details
          </button>
          {showDetails && (
            <div
              style={{
                backgroundColor: 'var(--dashboard-bg-secondary)',
                padding: '12px',
                borderRadius: '4px',
                fontSize: '12px',
                fontFamily: 'monospace',
                overflow: 'auto',
              }}
            >
              <div style={{ marginBottom: '8px' }}>
                <strong>HTTP Status:</strong> {error.httpStatus}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Request URL:</strong> {error.url}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Error Code:</strong> {error.code}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Error Message:</strong> {error.message}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Timestamp:</strong> {error.timestamp}
              </div>
              {error.rawBody && (
                <div style={{ marginTop: '8px' }}>
                  <strong>Raw Response:</strong>
                  <pre style={{ marginTop: '4px', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                    {error.rawBody}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
