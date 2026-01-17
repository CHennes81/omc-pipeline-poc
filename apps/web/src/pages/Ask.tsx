import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type {
  AskResponse,
  AskError,
  AskClarificationResponse,
  AskUnanswerableResponse,
  AskConfig,
} from '../api/client';
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

interface Message {
  id: string;
  role: 'user' | 'app';
  text: string;
  ts: number;
  kind?: 'normal' | 'clarification' | 'error';
}

export function AskPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draftText, setDraftText] = useState('');
  const [sessionContext, setSessionContext] = useState<Record<string, unknown> | null>(null);
  const [pendingClarification, setPendingClarification] = useState(false);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AskError | null>(null);
  const [showSupportedQuestions, setShowSupportedQuestions] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const productionCode = 'EXFTR'; // TODO: get from context

  // NL mode state
  const [askConfig, setAskConfig] = useState<AskConfig | null>(null);
  const [currentMode, setCurrentMode] = useState<'deterministic' | 'nl'>('deterministic');

  // Load Ask config on mount
  useEffect(() => {
    api
      .getAskConfig()
      .then((config) => {
        setAskConfig(config);
        // Set initial mode based on config
        if (config.default_mode === 'nl' && config.nl_enabled) {
          setCurrentMode('nl');
        }
      })
      .catch(() => {
        // If config fetch fails, stay in deterministic mode
        setAskConfig({ nl_enabled: false, dual_mode_ui: false, default_mode: 'deterministic' });
      });
  }, []);

  const handleAsk = async () => {
    if (!draftText.trim()) return;

    const userMessageText = draftText.trim();
    const isClarification = pendingClarification;

    // Log outgoing payload
    console.log('Ask request:', {
      question: userMessageText,
      is_clarification: isClarification,
      session_context: sessionContext,
    });

    // Add user message to chat
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: userMessageText,
      ts: Date.now(),
      kind: 'normal',
    };
    setMessages((prev) => [...prev, userMessage]);
    setDraftText(''); // Clear draft immediately

    try {
      setLoading(true);
      setError(null);

      const result = await api.askQuestion(
        productionCode,
        userMessageText, // Send ONLY the current draft text
        currentMode,
        sessionContext || undefined, // Use stored sessionContext
      );

      // Log routing status
      const routingStatus = 'status' in result ? result.status : 'ok';
      console.log('Routing status:', routingStatus);

      // Add app response as message bubble
      let appMessageText = '';
      let appMessageKind: 'normal' | 'clarification' | 'error' = 'normal';

      if ('status' in result) {
        if (result.status === 'needs_clarification') {
          const clarificationResult = result as AskClarificationResponse;
          appMessageText = clarificationResult.user_message || 'Could you provide more details?';
          appMessageKind = 'clarification';

          // Update sessionContext from response (replace, don't merge)
          setSessionContext({
            original_question: userMessageText,
            intent_id: clarificationResult.intent_id,
          });
          setPendingClarification(true);
          setResponse(null);
        } else if (result.status === 'unanswerable') {
          const unanswerableResult = result as AskUnanswerableResponse;
          appMessageText = unanswerableResult.message || 'Question could not be answered';
          appMessageKind = 'error';
          setSessionContext(null);
          setPendingClarification(false);
          setResponse(null);
        } else {
          // Normal response
          const normalResult = result as AskResponse;
          appMessageText = normalResult.answer || 'No answer provided';
          appMessageKind = 'normal';
          setResponse(normalResult);
          setSessionContext(null);
          setPendingClarification(false);
        }
      } else {
        // Fallback: assume normal response
        const normalResult = result as AskResponse;
        appMessageText = normalResult.answer || 'No answer provided';
        appMessageKind = 'normal';
        setResponse(normalResult);
        setSessionContext(null);
        setPendingClarification(false);
      }

      const appMessage: Message = {
        id: `app-${Date.now()}`,
        role: 'app',
        text: appMessageText,
        ts: Date.now(),
        kind: appMessageKind,
      };
      setMessages((prev) => [...prev, appMessage]);
    } catch (err) {
      // API client throws AskError objects
      let errorMessage = 'Failed to ask question';
      if (err && typeof err === 'object' && 'httpStatus' in err && 'code' in err) {
        const askError = err as AskError;
        setError(askError);
        errorMessage = askError.message || errorMessage;
      } else {
        // Fallback for unexpected error shapes
        const fallbackError: AskError = {
          httpStatus: 500,
          url: `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/ask`,
          code: 'unknown_error',
          message: err instanceof Error ? err.message : errorMessage,
          timestamp: new Date().toISOString(),
        };
        setError(fallbackError);
        errorMessage = fallbackError.message;
      }

      const errorMessageBubble: Message = {
        id: `app-error-${Date.now()}`,
        role: 'app',
        text: errorMessage,
        ts: Date.now(),
        kind: 'error',
      };
      setMessages((prev) => [...prev, errorMessageBubble]);
      setResponse(null);
      setSessionContext(null);
      setPendingClarification(false);
    } finally {
      setLoading(false);
    }
  };

  const handleModeSwitch = () => {
    const newMode = currentMode === 'deterministic' ? 'nl' : 'deterministic';
    setCurrentMode(newMode);
    // Clear previous results when switching modes
    setMessages([]);
    setDraftText('');
    setResponse(null);
    setSessionContext(null);
    setPendingClarification(false);
    setError(null);
  };

  const handleTemplateClick = (templateQuestion: string) => {
    setDraftText(templateQuestion);
  };

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 className="page-title">Ask</h1>

        {/* Mode switcher (only shown if dual-mode UI is enabled) */}
        {askConfig?.dual_mode_ui && askConfig?.nl_enabled && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', color: 'var(--dashboard-text-secondary)' }}>
              Mode:
            </span>
            <button
              onClick={handleModeSwitch}
              className="page-button-link"
              style={{ fontSize: '14px' }}
            >
              {currentMode === 'deterministic'
                ? 'Deterministic (switch to NL)'
                : 'Natural Language (switch to Deterministic)'}
            </button>
            {currentMode === 'nl' && (
              <span
                style={{ fontSize: '12px', color: 'var(--dashboard-accent)', marginLeft: '4px' }}
              >
                beta
              </span>
            )}
          </div>
        )}
      </div>

      <div className="ask-layout">
        {/* Left Column: Supported Questions + Input */}
        <div className="ask-left-column">
          <div className="page-section">
            <div
              className="ask-collapsible-header"
              onClick={() => setShowSupportedQuestions(!showSupportedQuestions)}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              <h2 style={{ margin: 0, display: 'inline-block' }}>
                {currentMode === 'nl' ? 'Sample Questions' : 'Supported Questions'}
              </h2>
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
                Click to view {currentMode === 'nl' ? 'sample' : 'supported'} questions
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

          {/* Chat messages */}
          <div
            className="page-section"
            style={{
              minHeight: '400px',
              maxHeight: '600px',
              overflowY: 'auto',
              marginBottom: '16px',
            }}
          >
            {messages.length === 0 ? (
              <p
                style={{
                  color: 'var(--dashboard-text-secondary)',
                  textAlign: 'center',
                  padding: '24px',
                }}
              >
                Start a conversation by asking a question
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      width: '100%',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '70%',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        backgroundColor:
                          msg.role === 'user'
                            ? 'var(--dashboard-accent)'
                            : msg.kind === 'error'
                              ? 'rgba(239, 68, 68, 0.1)'
                              : msg.kind === 'clarification'
                                ? 'rgba(255, 193, 7, 0.1)'
                                : 'var(--dashboard-surface)',
                        border:
                          msg.role === 'user'
                            ? 'none'
                            : msg.kind === 'error'
                              ? '1px solid rgba(239, 68, 68, 0.3)'
                              : msg.kind === 'clarification'
                                ? '1px solid rgba(255, 193, 7, 0.3)'
                                : '1px solid var(--dashboard-border)',
                        color:
                          msg.role === 'user'
                            ? 'white'
                            : msg.kind === 'error'
                              ? '#fca5a5'
                              : 'var(--dashboard-text-primary)',
                        fontSize: '14px',
                        lineHeight: '1.5',
                        wordWrap: 'break-word',
                      }}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <div
                      style={{
                        padding: '12px 16px',
                        borderRadius: '12px',
                        backgroundColor: 'var(--dashboard-surface)',
                        border: '1px solid var(--dashboard-border)',
                        color: 'var(--dashboard-text-secondary)',
                        fontSize: '14px',
                      }}
                    >
                      Thinking...
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Input area */}
          <div className="page-section">
            <label className="page-label">
              <strong>{pendingClarification ? 'Clarification:' : 'Question:'}</strong>
              <textarea
                value={draftText}
                onChange={(e) => setDraftText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    handleAsk();
                  }
                }}
                className="page-textarea"
                placeholder={
                  pendingClarification
                    ? 'Provide clarification...'
                    : currentMode === 'nl'
                      ? 'Ask your question in natural language...'
                      : 'Enter your question or select from supported questions above'
                }
                style={{ minHeight: '80px' }}
              />
            </label>
            <button
              onClick={handleAsk}
              disabled={loading || !draftText.trim()}
              className="page-button"
            >
              {loading ? 'Asking...' : pendingClarification ? 'Send Clarification' : 'Ask'}
            </button>
          </div>
        </div>

        {/* Right Column: Results (for final answers with evidence) */}
        <div className="ask-right-column">
          {error && <AskErrorPanel error={error} />}

          {response && (
            <div className="ask-results">
              <div className="page-section">
                <h2>Answer</h2>
                <div className="page-info-box">
                  <AnswerText text={response?.answer || 'No answer provided'} />
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
                {response?.evidence &&
                  Object.entries(response.evidence).map(([key, items]) => {
                    // Defensive check: ensure items is an array
                    if (!Array.isArray(items)) {
                      return null;
                    }

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
