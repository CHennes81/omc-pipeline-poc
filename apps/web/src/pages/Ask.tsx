import { useState } from 'react';
import { api } from '../api/client';
import type { AskResponse } from '../api/client';
import { ExplanationDialog } from '../components/ExplanationDialog';
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
  const [error, setError] = useState<string | null>(null);
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
      setError(err instanceof Error ? err.message : 'Failed to ask question');
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
          {error && <div className="page-error">Error: {error}</div>}

          {response && (
            <div className="ask-results">
              <div className="page-section">
                <h2>Answer</h2>
                <div className="page-info-box">{response.answer}</div>
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
                  <h2 style={{ margin: 0 }}>Audit Trail</h2>
                  <button
                    onClick={() => setShowExplanation(true)}
                    className="page-button-link"
                    style={{ fontSize: '13px' }}
                  >
                    Show details
                  </button>
                </div>
                {Object.entries(response.evidence).map(([key, items]) => (
                  <div key={key} className="audit-trail-group" style={{ marginBottom: '24px' }}>
                    <h3>{key}</h3>
                    {items.length > 0 ? (
                      <div className="audit-trail-items">
                        {items.map((item: unknown, idx: number) => {
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
                                  {otherFields.map(([fieldKey, val]) => (
                                    <div key={fieldKey} className="audit-trail-field">
                                      <span className="audit-trail-field-label">{fieldKey}:</span>
                                      <span className="audit-trail-field-value">
                                        {val !== null && val !== undefined ? String(val) : '-'}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              )}
                              {storageUri && (
                                <div className="audit-trail-uri">
                                  <span className="audit-trail-field-label">Storage URI:</span>
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
                        })}
                      </div>
                    ) : (
                      <p className="page-empty">No audit trail found</p>
                    )}
                  </div>
                ))}
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
