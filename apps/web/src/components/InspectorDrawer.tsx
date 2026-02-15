import { useState, useCallback } from 'react';
import { useInspector } from '../context/inspector-context';
import './InspectorDrawer.css';

export function InspectorDrawer() {
  const { isOpen, setOpen, payload } = useInspector();
  const [activeTab, setActiveTab] = useState<'overview' | 'raw'>('overview');

  const rawJson = payload !== null && payload !== undefined ? JSON.stringify(payload, null, 2) : '';

  const handleCopy = useCallback(() => {
    if (rawJson) {
      void navigator.clipboard.writeText(rawJson);
    }
  }, [rawJson]);

  if (!isOpen) return null;

  return (
    <>
      <div className="inspector-backdrop" onClick={() => setOpen(false)} aria-hidden="true" />
      <aside className="inspector-drawer" role="complementary" aria-label="Metadata Inspector">
        <div className="inspector-header">
          <h2 className="inspector-title">Inspector</h2>
          <button
            type="button"
            className="inspector-close"
            onClick={() => setOpen(false)}
            aria-label="Close inspector"
          >
            ×
          </button>
        </div>

        <div className="inspector-tabs">
          <button
            type="button"
            className={`inspector-tab ${activeTab === 'overview' ? 'inspector-tab-active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            type="button"
            className={`inspector-tab ${activeTab === 'raw' ? 'inspector-tab-active' : ''}`}
            onClick={() => setActiveTab('raw')}
          >
            Raw
          </button>
        </div>

        <div className="inspector-content">
          {payload === null || payload === undefined ? (
            <p className="inspector-empty">No object selected to inspect.</p>
          ) : activeTab === 'overview' ? (
            <OverviewTab payload={payload} />
          ) : (
            <div className="inspector-raw-wrapper">
              <div className="inspector-raw-actions">
                <button
                  type="button"
                  className="inspector-copy-btn"
                  onClick={handleCopy}
                  disabled={!rawJson}
                >
                  Copy JSON
                </button>
              </div>
              <pre className="inspector-raw-pre">{rawJson || '{}'}</pre>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

function OverviewTab({ payload }: { payload: unknown }) {
  const entries = toKeyValueEntries(payload);
  if (entries.length === 0) {
    return <p className="inspector-empty">No displayable fields.</p>;
  }
  return (
    <dl className="inspector-overview-dl">
      {entries.map(([key, value]) => (
        <div key={String(key)} className="inspector-overview-row">
          <dt className="inspector-overview-dt">{String(key)}</dt>
          <dd className="inspector-overview-dd">{formatOverviewValue(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

function toKeyValueEntries(obj: unknown): [string, unknown][] {
  if (obj === null || obj === undefined) return [];
  if (typeof obj !== 'object') return [];
  if (Array.isArray(obj)) return [['[array]', `Array(${obj.length})`]];
  return Object.entries(obj).filter(([, v]) => v !== null && v !== undefined && v !== '');
}

function formatOverviewValue(value: unknown): string {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return `[array, ${value.length} items]`;
  if (typeof value === 'object') return '[object]';
  return String(value);
}
