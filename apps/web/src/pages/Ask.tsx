import { useState } from 'react';
import { api } from '../api/client';
import type { AskResponse } from '../api/client';

const TEMPLATE_QUESTIONS = [
  { template: 'latest_camera_original', question: 'What is the latest camera original for shot 011_021?' },
  { template: 'lineage_chain_to_latest_edit_export', question: 'Show lineage chain to latest edit export for shot 011_021' },
  { template: 'shots_with_dailies_no_edit_export', question: 'Which shots have dailies but no edit export?' },
  { template: 'shots_ready_for_turnover_and_missing', question: 'Which shots are ready for turnover but missing?' },
  { template: 'source_relink_keys', question: 'What are the relink keys for shot 011_021?' },
  { template: 'latest_versions_by_type', question: 'Show latest versions by type for shot 011_021' },
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
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ marginBottom: '16px' }}>
        <a href="/" style={{ color: '#0066cc' }}>← Back to Dashboard</a>
      </div>

      <h1>Ask</h1>

      <div style={{ marginBottom: '24px' }}>
        <h2>Supported Questions</h2>
        <ul>
          {TEMPLATE_QUESTIONS.map((item, idx) => (
            <li key={idx} style={{ marginBottom: '8px' }}>
              <button
                onClick={() => handleTemplateClick(item.question)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#0066cc',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  padding: 0,
                }}
              >
                {item.question}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <label>
          <strong>Question:</strong>
          <br />
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={{
              width: '100%',
              minHeight: '100px',
              padding: '8px',
              fontSize: '14px',
              fontFamily: 'inherit',
              marginTop: '8px',
            }}
            placeholder="Enter your question or select from supported questions above"
          />
        </label>
        <br />
        <button
          onClick={handleAsk}
          disabled={loading || !question.trim()}
          style={{
            marginTop: '12px',
            padding: '10px 20px',
            fontSize: '16px',
            cursor: loading ? 'wait' : 'pointer',
          }}
        >
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </div>

      {error && (
        <div style={{ padding: '12px', background: '#fee', border: '1px solid #fcc', marginBottom: '16px' }}>
          Error: {error}
        </div>
      )}

      {response && (
        <div>
          <h2>Answer</h2>
          <div style={{ padding: '16px', background: '#f9f9f9', border: '1px solid #ddd', marginBottom: '16px' }}>
            {response.answer}
          </div>

          <h2>Evidence</h2>
          {Object.entries(response.evidence).map(([key, items]) => (
            <div key={key} style={{ marginBottom: '24px' }}>
              <h3>{key}</h3>
              {items.length > 0 ? (
                <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                  <thead>
                    <tr style={{ background: '#f0f0f0' }}>
                      {Object.keys(items[0]).map(col => (
                        <th key={col} style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item: any, idx: number) => (
                      <tr key={idx}>
                        {Object.values(item).map((val: any, colIdx: number) => (
                          <td key={colIdx} style={{ padding: '8px', border: '1px solid #ddd', fontFamily: typeof val === 'string' && val.length > 50 ? 'monospace' : 'inherit', fontSize: typeof val === 'string' && val.length > 50 ? '12px' : 'inherit' }}>
                            {val !== null && val !== undefined ? String(val) : '-'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No evidence found</p>
              )}
            </div>
          ))}

          <h2>Explanation</h2>
          <div style={{ padding: '16px', background: '#f0f8ff', border: '1px solid #b0d4ff' }}>
            <p><strong>Template:</strong> {response.template}</p>
            <p><strong>Parameters:</strong> {JSON.stringify(response.params, null, 2)}</p>
            <p><strong>Query:</strong> {response.explanation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
