import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import type { ShotDetail, Version, Event, LineageNode } from '../api/client';
import './PageStyles.css';

export function ShotDetailPage() {
  const { shotCode } = useParams<{ shotCode: string }>();
  const [shot, setShot] = useState<ShotDetail | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [lineage, setLineage] = useState<LineageNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const productionCode = 'EXFTR'; // TODO: get from context or route

  useEffect(() => {
    if (shotCode) {
      loadShotData();
    }
  }, [shotCode]);

  const loadShotData = async () => {
    if (!shotCode) return;
    try {
      setLoading(true);
      const [shotData, eventsData, lineageData] = await Promise.all([
        api.getShotDetail(shotCode, productionCode),
        api.getShotEvents(shotCode, productionCode),
        api.getShotLineage(shotCode, productionCode),
      ]);
      setShot(shotData.shot);
      setEvents(eventsData.events);
      setLineage(lineageData.chain);
      // TODO: Load versions separately - need asset_id
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load shot data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="page-loading">Loading...</div>;
  if (error) return <div className="page-error">Error: {error}</div>;
  if (!shot) return <div className="page-empty">Shot not found</div>;

  // Group versions by type
  const versionsByType: Record<string, Version[]> = {};
  versions.forEach((v) => {
    if (!versionsByType[v.version_type]) {
      versionsByType[v.version_type] = [];
    }
    versionsByType[v.version_type].push(v);
  });

  return (
    <div className="page-container">
      <div style={{ marginBottom: '16px' }}>
        <a href="/" className="page-back-link">
          ← Back to Dashboard
        </a>
      </div>

      <h1 className="page-title">Shot: {shot.shot_code}</h1>
      <div className="page-section">
        <p>
          <strong>Scene:</strong> {shot.scene || '-'}
        </p>
        <p>
          <strong>Description:</strong> {shot.description || '-'}
        </p>
      </div>

      <div className="page-section">
        <h2>Versions</h2>
        {Object.keys(versionsByType).length > 0 ? (
          Object.entries(versionsByType).map(([type, vers]) => (
            <div key={type} style={{ marginBottom: '24px' }}>
              <h3>{type}</h3>
              <table className="page-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Storage URI</th>
                    <th>Codec</th>
                    <th>FPS</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {vers.map((v) => (
                    <tr key={v.id}>
                      <td className="monospace">{v.id.substring(0, 8)}...</td>
                      <td>{v.storage_uri}</td>
                      <td>{v.codec || '-'}</td>
                      <td>{v.fps || '-'}</td>
                      <td>{new Date(v.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))
        ) : (
          <p className="page-empty">No versions found</p>
        )}
      </div>

      <div className="page-section">
        <h2>Lineage</h2>
        {lineage.length > 0 ? (
          <div style={{ marginBottom: '24px' }}>
            {lineage.map((node, idx) => (
              <div key={node.version_id} style={{ marginBottom: '8px' }}>
                {idx > 0 && (
                  <div style={{ marginLeft: '20px', color: 'var(--dashboard-text-secondary)' }}>
                    ↓
                  </div>
                )}
                <div className="page-list-item">
                  <strong>{node.version_type}</strong> ({node.version_id.substring(0, 8)}...)
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="page-empty">No lineage data</p>
        )}
      </div>

      <div className="page-section">
        <h2>Events Timeline</h2>
        {events.length > 0 ? (
          <table className="page-table">
            <thead>
              <tr>
                <th>Event Type</th>
                <th>Actor</th>
                <th>Tool</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td>{event.event_type}</td>
                  <td>{event.actor || '-'}</td>
                  <td>{event.tool || '-'}</td>
                  <td>{new Date(event.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="page-empty">No events</p>
        )}
      </div>
    </div>
  );
}
