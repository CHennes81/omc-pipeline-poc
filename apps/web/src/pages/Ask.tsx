import { useState } from 'react';
import { api } from '../api/client';
import type { AskResponse, AskError } from '../api/client';
import { ExplanationDialog } from '../components/ExplanationDialog';
import { AnswerText } from '../components/AnswerText';
import { VersionAuditCard } from '../components/VersionAuditCard';
import { ShotsAuditCard } from '../components/ShotsAuditCard';
import { AskErrorPanel } from '../components/AskErrorPanel';
import { formatDateTime } from '../utils/formatting';
import './PageStyles.css';

const TEMPLATE_QUESTIONS = [
  {
    template: 'latest_camera_original',
    question: 'What is the latest camera original for shot 011_021?',
  },
  {
    template: 'lineage_chain_to_latest_edit_export',
    question: 'Show lineage chain to latest edit export for shot 011_021',
  },
  {
    template: 'shots_with_dailies_no_edit_export',
    question: 'Which shots have dailies but no edit export?',
  },
  {
    template: 'shots_ready_for_turnover_and_missing',
    question: 'Which shots are ready for turnover but missing?',
  },
  { template: 'source_relink_keys', question: 'What are the relink keys for shot 011_021?' },
  {
    template: 'latest_versions_by_type',
    question: 'Show latest versions by type for shot 011_021',
  },
  { template: 'archive_status', question: 'What is the archive status for production EXFTR?' },
];

export function AskPage() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AskError | null>(null);
  const [showSupportedQuestions, setShowSupportedQuestions] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const productionCode = 'EXFTR'; // TODO: get from context

  const handleAsk = async () => {
    if (!question.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const result = await api.askQuestion(productionCode, question);
      setResponse(result);
    } catch (err) {
      // API client throws AskError objects
      if (err && typeof err === 'object' && 'httpStatus' in err && 'code' in err) {
        setError(err as AskError);
      } else {
        // Fallback for unexpected error shapes
        setError({
          httpStatus: 500,
          url: `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/ask`,
          code: 'unknown_error',
          message: err instanceof Error ? err.message : 'Failed to ask question',
          timestamp: new Date().toISOString(),
        });
      }
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateClick = (templateQuestion: string) => {
    setQuestion(templateQuestion);
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Ask</h1>

      <div className="ask-layout">
        {/* Left Column: Supported Questions + Input */}
        <div className="ask-left-column">
          <div className="page-section">
            <div
              className="ask-collapsible-header"
              onClick={() => setShowSupportedQuestions(!showSupportedQuestions)}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              <h2 style={{ margin: 0, display: 'inline-block' }}>Supported Questions</h2>
              <span style={{ marginLeft: '12px', color: 'var(--dashboard-accent)' }}>
                {showSupportedQuestions ? 'Hide' : 'Show'}
              </span>
            </div>
            {!showSupportedQuestions && (
              <p
                style={{
                  marginTop: '8px',
                  color: 'var(--dashboard-text-secondary)',
                  fontSize: '14px',
                }}
              >
                Click to view supported questions
              </p>
            )}
            {showSupportedQuestions && (
              <ul style={{ listStyle: 'none', padding: 0, marginTop: '12px' }}>
                {TEMPLATE_QUESTIONS.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: '8px' }}>
                    <button
                      onClick={() => handleTemplateClick(item.question)}
                      className="page-button-link"
                    >
                      {item.question}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="page-section">
            <label className="page-label">
              <strong>Question:</strong>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="page-textarea"
                placeholder="Enter your question or select from supported questions above"
              />
            </label>
            <button
              onClick={handleAsk}
              disabled={loading || !question.trim()}
              className="page-button"
            >
              {loading ? 'Asking...' : 'Ask'}
            </button>
          </div>
        </div>

        {/* Right Column: Results */}
        <div className="ask-right-column">
          {error && <AskErrorPanel error={error} />}

          {response && (
            <div className="ask-results">
              <div className="page-section">
                <h2>Answer</h2>
                <div className="page-info-box">
                  <AnswerText text={response.answer} />
                </div>
              </div>

              <div className="page-section">
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '16px',
                  }}
                >
                  <h2 style={{ margin: 0 }}>Audit Information</h2>
                  <button
                    onClick={() => setShowExplanation(true)}
                    className="page-button-link"
                    style={{ fontSize: '13px' }}
                  >
                    Show details
                  </button>
                </div>
                {Object.entries(response.evidence).map(([key, items]) => {
                  // Check if this is a "versions" evidence group
                  const isVersionsEvidence =
                    key.toLowerCase() === 'versions' ||
                    key.toLowerCase().includes('version') ||
                    items.some(
                      (item: unknown) =>
                        typeof item === 'object' &&
                        item !== null &&
                        (Object.keys(item as Record<string, unknown>).some(
                          (k) =>
                            k.toLowerCase() === 'version_type' ||
                            k.toLowerCase() === 'version type' ||
                            k.toLowerCase() === 'version_id' ||
                            k.toLowerCase() === 'version id',
                        ) ||
                          Object.values(item as Record<string, unknown>).some(
                            (val) =>
                              typeof val === 'string' &&
                              /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
                                val,
                              ),
                          )),
                    );

                  // Check if this is a "shots" evidence group
                  const isShotsEvidence =
                    key.toLowerCase() === 'shots' ||
                    key.toLowerCase().includes('shot') ||
                    items.some(
                      (item: unknown) =>
                        typeof item === 'object' &&
                        item !== null &&
                        (Object.keys(item as Record<string, unknown>).some(
                          (k) =>
                            k.toLowerCase() === 'shot_code' ||
                            k.toLowerCase() === 'shot code' ||
                            k.toLowerCase() === 'shotcode',
                        ) ||
                          Object.values(item as Record<string, unknown>).some(
                            (val) => typeof val === 'string' && /^\d{3}_\d{3}$/.test(val),
                          )),
                    );

                  return (
                    <div key={key} className="audit-trail-group" style={{ marginBottom: '24px' }}>
                      <h3>{key}</h3>
                      {items.length > 0 ? (
                        <div className="audit-trail-items">
                          {/* Use ShotsAuditCard for shots evidence */}
                          {isShotsEvidence ? (
                            <ShotsAuditCard shots={items as Array<Record<string, unknown>>} />
                          ) : isVersionsEvidence ? (
                            // Use VersionAuditCard for versions evidence
                            items.map((item: unknown, idx: number) => {
                              if (typeof item !== 'object' || item === null) {
                                return null;
                              }
                              return (
                                <VersionAuditCard
                                  key={idx}
                                  version={item as Record<string, unknown>}
                                />
                              );
                            })
                          ) : (
                            // Fallback to generic audit trail for other evidence
                            items.map((item: unknown, idx: number) => {
                              if (typeof item !== 'object' || item === null) {
                                return null;
                              }
                              const itemRecord = item as Record<string, unknown>;
                              const storageUri =
                                itemRecord['storage_uri'] ||
                                itemRecord['Storage URI'] ||
                                itemRecord['storageURI'];
                              const otherFields = Object.entries(itemRecord).filter(
                                ([k]) =>
                                  k.toLowerCase() !== 'storage_uri' &&
                                  k !== 'Storage URI' &&
                                  k !== 'storageURI',
                              );

                              return (
                                <div key={idx} className="audit-trail-item">
                                  {otherFields.length > 0 && (
                                    <div className="audit-trail-metadata">
                                      {otherFields.map(([fieldKey, val]) => {
                                        const isDateField =
                                          fieldKey.toLowerCase() === 'created_at' ||
                                          fieldKey.toLowerCase() === 'created at' ||
                                          fieldKey.toLowerCase() === 'createdat';
                                        const displayValue: string =
                                          isDateField && val !== null && val !== undefined
                                            ? formatDateTime(String(val))
                                            : val !== null && val !== undefined
                                              ? String(val)
                                              : '-';
                                        return (
                                          <div key={fieldKey} className="audit-trail-field">
                                            <span className="audit-trail-field-label">
                                              {fieldKey}:
                                            </span>
                                            <span className="audit-trail-field-value">
                                              {displayValue}
                                            </span>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  )}
                                  {storageUri != null && String(storageUri).trim() !== '' && (
                                    <div className="audit-trail-uri">
                                      <span className="audit-trail-field-label">Locator:</span>
                                      <a
                                        href={String(storageUri)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="audit-trail-uri-link"
                                      >
                                        {String(storageUri)}
                                      </a>
                                    </div>
                                  )}
                                </div>
                              );
                            })
                          )}
                        </div>
                      ) : (
                        <p className="page-empty">No audit information found</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      <ExplanationDialog
        open={showExplanation}
        onClose={() => setShowExplanation(false)}
        response={response}
      />
    </div>
  );
}
