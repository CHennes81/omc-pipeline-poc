import { useEffect } from 'react';
import type { AskResponse } from '../api/client';

interface ExplanationDialogProps {
  open: boolean;
  onClose: () => void;
  response: AskResponse | null;
}

export function ExplanationDialog({ open, onClose, response }: ExplanationDialogProps) {
  useEffect(() => {
    if (!open) return;
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [open, onClose]);

  if (!open || !response) return null;

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="explanation-title"
      onClick={onClose}
    >
      <div
        className="modal-card"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '600px' }}
      >
        <h2 id="explanation-title">Explanation</h2>
        <div style={{ lineHeight: 1.6 }}>
          <p>
            <strong>Template:</strong> {response.template}
          </p>
          <p>
            <strong>Parameters:</strong>
          </p>
          <pre
            style={{
              background: 'var(--dashboard-surface)',
              padding: '12px',
              borderRadius: '6px',
              overflow: 'auto',
              fontSize: '13px',
              marginTop: '8px',
            }}
          >
            {JSON.stringify(response.params, null, 2)}
          </pre>
          <p style={{ marginTop: '16px' }}>
            <strong>Query:</strong>
          </p>
          <pre
            style={{
              background: 'var(--dashboard-surface)',
              padding: '12px',
              borderRadius: '6px',
              overflow: 'auto',
              fontSize: '13px',
              marginTop: '8px',
              whiteSpace: 'pre-wrap',
            }}
          >
            {response.explanation}
          </pre>
        </div>
        <div className="modal-actions">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
