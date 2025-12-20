import { useState, useEffect } from 'react';
import { api, Production, ShotSummary } from '../api/client';

export function Dashboard() {
  const [productions, setProductions] = useState<Production[]>([]);
  const [selectedProduction, setSelectedProduction] = useState<string>('');
  const [shots, setShots] = useState<ShotSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stageCounts, setStageCounts] = useState<Record<string, number>>({});
  const [blockedShots, setBlockedShots] = useState<ShotSummary[]>([]);

  useEffect(() => {
    loadProductions();
  }, []);

  useEffect(() => {
    if (selectedProduction) {
      loadShots(selectedProduction);
    }
  }, [selectedProduction]);

  useEffect(() => {
    if (shots.length > 0) {
      // Calculate stage counts
      const counts: Record<string, number> = {};
      shots.forEach(shot => {
        counts[shot.stage] = (counts[shot.stage] || 0) + 1;
      });
      setStageCounts(counts);

      // Identify blocked shots (has dailies but no edit export)
      const blocked = shots.filter(shot => {
        // This is a simplified check - in real app, would query events
        return shot.stage === 'DAILIES' || (shot.stage === 'EDIT_EXPORT' && !shot.stage.includes('TURNOVER'));
      });
      setBlockedShots(blocked);
    }
  }, [shots]);

  const loadProductions = async () => {
    try {
      setLoading(true);
      const data = await api.getProductions();
      setProductions(data.productions);
      if (data.productions.length > 0) {
        setSelectedProduction(data.productions[0].code);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load productions');
    } finally {
      setLoading(false);
    }
  };

  const loadShots = async (productionCode: string) => {
    try {
      setLoading(true);
      const data = await api.getShots(productionCode);
      setShots(data.shots);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load shots');
    } finally {
      setLoading(false);
    }
  };

  const stages = ['NEW', 'CAPTURE', 'OFFLOAD', 'DAILIES', 'EDIT_EXPORT', 'TURNOVER', 'ARCHIVE'];

  return (
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <h1>Dashboard</h1>

      {error && (
        <div style={{ padding: '12px', background: '#fee', border: '1px solid #fcc', marginBottom: '16px' }}>
          Error: {error}
        </div>
      )}

      <div style={{ marginBottom: '24px' }}>
        <label>
          Production:{' '}
          <select
            value={selectedProduction}
            onChange={(e) => setSelectedProduction(e.target.value)}
            style={{ padding: '8px', fontSize: '14px' }}
          >
            {productions.map(p => (
              <option key={p.code} value={p.code}>{p.title} ({p.code})</option>
            ))}
          </select>
        </label>
      </div>

      {loading && <div>Loading...</div>}

      {!loading && shots.length > 0 && (
        <>
          <h2>Shots by Stage</h2>
          <table style={{ borderCollapse: 'collapse', width: '100%', marginBottom: '24px' }}>
            <thead>
              <tr style={{ background: '#f0f0f0' }}>
                <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Stage</th>
                <th style={{ padding: '8px', textAlign: 'right', border: '1px solid #ddd' }}>Count</th>
              </tr>
            </thead>
            <tbody>
              {stages.map(stage => (
                <tr key={stage}>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{stage}</td>
                  <td style={{ padding: '8px', textAlign: 'right', border: '1px solid #ddd' }}>
                    {stageCounts[stage] || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>Blocked Shots</h2>
          {blockedShots.length > 0 ? (
            <table style={{ borderCollapse: 'collapse', width: '100%', marginBottom: '24px' }}>
              <thead>
                <tr style={{ background: '#f0f0f0' }}>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Shot Code</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Scene</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Stage</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Reason</th>
                </tr>
              </thead>
              <tbody>
                {blockedShots.map(shot => (
                  <tr key={shot.shot_code}>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                      <a href={`/shot/${shot.shot_code}`} style={{ color: '#0066cc' }}>
                        {shot.shot_code}
                      </a>
                    </td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{shot.scene || '-'}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{shot.stage}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                      {shot.stage === 'DAILIES' ? 'Has dailies but missing edit export' : 'Ready for turnover'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No blocked shots</p>
          )}

          <h2>All Shots</h2>
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr style={{ background: '#f0f0f0' }}>
                <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Shot Code</th>
                <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Scene</th>
                <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Stage</th>
              </tr>
            </thead>
            <tbody>
              {shots.map(shot => (
                <tr key={shot.shot_code}>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                    <a href={`/shot/${shot.shot_code}`} style={{ color: '#0066cc' }}>
                      {shot.shot_code}
                    </a>
                  </td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{shot.scene || '-'}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{shot.stage}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
