import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import type { ShotDetail, Version, Event, LineageNode } from '../api/client';

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

  if (loading) return <div style={{ padding: '24px' }}>Loading...</div>;
  if (error) return <div style={{ padding: '24px', color: 'red' }}>Error: {error}</div>;
  if (!shot) return <div style={{ padding: '24px' }}>Shot not found</div>;

  // Group versions by type
  const versionsByType: Record<string, Version[]> = {};
  versions.forEach(v => {
    if (!versionsByType[v.version_type]) {
      versionsByType[v.version_type] = [];
    }
    versionsByType[v.version_type].push(v);
  });

  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ marginBottom: '16px' }}>
        <a href="/" style={{ color: '#0066cc' }}>← Back to Dashboard</a>
      </div>

      <h1>Shot: {shot.shot_code}</h1>
      <div style={{ marginBottom: '24px' }}>
        <p><strong>Scene:</strong> {shot.scene || '-'}</p>
        <p><strong>Description:</strong> {shot.description || '-'}</p>
      </div>

      <h2>Versions</h2>
      {Object.keys(versionsByType).length > 0 ? (
        Object.entries(versionsByType).map(([type, vers]) => (
          <div key={type} style={{ marginBottom: '24px' }}>
            <h3>{type}</h3>
            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr style={{ background: '#f0f0f0' }}>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>ID</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Storage URI</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Codec</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>FPS</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Created</th>
                </tr>
              </thead>
              <tbody>
                {vers.map(v => (
                  <tr key={v.id}>
                    <td style={{ padding: '8px', border: '1px solid #ddd', fontFamily: 'monospace', fontSize: '12px' }}>
                      {v.id.substring(0, 8)}...
                    </td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{v.storage_uri}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{v.codec || '-'}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{v.fps || '-'}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                      {new Date(v.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))
      ) : (
        <p>No versions found</p>
      )}

      <h2>Lineage</h2>
      {lineage.length > 0 ? (
        <div style={{ marginBottom: '24px' }}>
          {lineage.map((node, idx) => (
            <div key={node.version_id} style={{ marginBottom: '8px' }}>
              {idx > 0 && <div style={{ marginLeft: '20px' }}>↓</div>}
              <div style={{ padding: '8px', background: '#f9f9f9', border: '1px solid #ddd' }}>
                <strong>{node.version_type}</strong> ({node.version_id.substring(0, 8)}...)
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p>No lineage data</p>
      )}

      <h2>Events Timeline</h2>
      {events.length > 0 ? (
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr style={{ background: '#f0f0f0' }}>
              <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Event Type</th>
              <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Actor</th>
              <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Tool</th>
              <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Created</th>
            </tr>
          </thead>
          <tbody>
            {events.map(event => (
              <tr key={event.id}>
                <td style={{ padding: '8px', border: '1px solid #ddd' }}>{event.event_type}</td>
                <td style={{ padding: '8px', border: '1px solid #ddd' }}>{event.actor || '-'}</td>
                <td style={{ padding: '8px', border: '1px solid #ddd' }}>{event.tool || '-'}</td>
                <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                  {new Date(event.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No events</p>
      )}
    </div>
  );
}
