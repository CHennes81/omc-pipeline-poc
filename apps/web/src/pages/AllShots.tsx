import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Production, ShotSummary } from '../api/client';
import { CardSection } from '../components/CardSection';
import './Dashboard.css';

export function AllShots() {
  const [productions, setProductions] = useState<Production[]>([]);
  const [selectedProduction, setSelectedProduction] = useState<string>('');
  const [shots, setShots] = useState<ShotSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProductions();
  }, []);

  useEffect(() => {
    if (selectedProduction) {
      loadShots(selectedProduction);
    }
  }, [selectedProduction]);

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

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">All Shots</h1>

        <div className="dashboard-controls">
          <div className="production-selector">
            <label htmlFor="production-select">Production:</label>
            <select
              id="production-select"
              value={selectedProduction}
              onChange={(e) => setSelectedProduction(e.target.value)}
            >
              {productions.map((p) => (
                <option key={p.code} value={p.code}>
                  {p.title} ({p.code})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {error && <div className="error-message">Error: {error}</div>}

      {loading && <div className="loading-state">Loading...</div>}

      {!loading && shots.length > 0 && (
        <CardSection
          title="All Shots"
          subtitle={`${shots.length} total shot${shots.length !== 1 ? 's' : ''}`}
        >
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Shot Code</th>
                  <th>Scene</th>
                  <th>Stage</th>
                </tr>
              </thead>
              <tbody>
                {shots.map((shot) => (
                  <tr key={shot.shot_code}>
                    <td>{shot.description || '-'}</td>
                    <td>
                      <a href={`/shot/${shot.shot_code}`}>{shot.shot_code}</a>
                    </td>
                    <td>{shot.scene || '-'}</td>
                    <td>
                      <span className="stage-badge" data-stage={shot.stage}>
                        {shot.stage.replace(/_/g, ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardSection>
      )}

      {!loading && shots.length === 0 && selectedProduction && (
        <CardSection title="All Shots">
          <div className="empty-state">No shots found for this production</div>
        </CardSection>
      )}
    </div>
  );
}
