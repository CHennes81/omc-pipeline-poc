import { useState } from 'react';
import { api } from '../api/client';
import type { AskResponse } from '../api/client';
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

      <div className="page-section">
        <h2>Supported Questions</h2>
        <ul style={{ listStyle: 'none', padding: 0 }}>
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
        <button onClick={handleAsk} disabled={loading || !question.trim()} className="page-button">
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </div>

      {error && <div className="page-error">Error: {error}</div>}

      {response && (
        <div>
          <div className="page-section">
            <h2>Answer</h2>
            <div className="page-info-box">{response.answer}</div>
          </div>

          <div className="page-section">
            <h2>Evidence</h2>
            {Object.entries(response.evidence).map(([key, items]) => (
              <div key={key} style={{ marginBottom: '24px' }}>
                <h3>{key}</h3>
                {items.length > 0 ? (
                  <table className="page-table">
                    <thead>
                      <tr>
                        {Object.keys(items[0]).map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((item: any, idx: number) => (
                        <tr key={idx}>
                          {Object.values(item).map((val: any, colIdx: number) => (
                            <td
                              key={colIdx}
                              className={
                                typeof val === 'string' && val.length > 50 ? 'monospace' : ''
                              }
                            >
                              {val !== null && val !== undefined ? String(val) : '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="page-empty">No evidence found</p>
                )}
              </div>
            ))}
          </div>

          <div className="page-section">
            <h2>Explanation</h2>
            <div className="page-info-box-light">
              <p>
                <strong>Template:</strong> {response.template}
              </p>
              <p>
                <strong>Parameters:</strong> {JSON.stringify(response.params, null, 2)}
              </p>
              <p>
                <strong>Query:</strong> {response.explanation}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
