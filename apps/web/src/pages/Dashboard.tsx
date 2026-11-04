import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Production, ShotSummary } from '../api/client';
import { StagePill } from '../components/StagePill';
import { CardSection } from '../components/CardSection';
import './Dashboard.css';

export function Dashboard() {
  const [productions, setProductions] = useState<Production[]>([]);
  const [selectedProduction, setSelectedProduction] = useState<string>('');
  const [shots, setShots] = useState<ShotSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stageCounts, setStageCounts] = useState<Record<string, number>>({});
  const [blockedShots, setBlockedShots] = useState<ShotSummary[]>([]);
  const [stageFilter, setStageFilter] = useState<string>('ALL');

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
      shots.forEach((shot) => {
        counts[shot.stage] = (counts[shot.stage] || 0) + 1;
      });
      setStageCounts(counts);

      // Identify blocked shots (has dailies but no edit export)
      const blocked = shots.filter((shot) => {
        // This is a simplified check - in real app, would query events
        return (
          shot.stage === 'DAILIES' ||
          (shot.stage === 'EDIT_EXPORT' && !shot.stage.includes('TURNOVER'))
        );
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
      setStageFilter('ALL'); // a stage filter from another production may be empty here
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load shots');
    } finally {
      setLoading(false);
    }
  };

  // Filter out NEW stage from display (but keep it in computation)
  const displayStages = [
    'CAPTURE',
    'CAMERA_MASTER',
    'DAILIES',
    'EDIT_EXPORT',
    'TURNOVER',
    'ARCHIVE',
  ];

  // 'ALL' = the default "All Pending" view; otherwise a single stage filter.
  const ALL = 'ALL';
  const stageLabel = (stage: string) => stage.replace(/_/g, ' ');
  const titleCase = (text: string) =>
    text.toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase());

  const visibleShots =
    stageFilter === ALL ? blockedShots : shots.filter((shot) => shot.stage === stageFilter);

  // DAILIES and EDIT_EXPORT shots are "pending activities"; other stages are plain stage listings.
  const isPendingView =
    stageFilter === ALL || stageFilter === 'DAILIES' || stageFilter === 'EDIT_EXPORT';
  const listTitle = isPendingView
    ? 'Pending Activities'
    : `Shots in ${titleCase(stageLabel(stageFilter))}`;
  const listSubtitle =
    visibleShots.length > 0
      ? isPendingView
        ? `${visibleShots.length} shot${visibleShots.length !== 1 ? 's' : ''} with pending work`
        : `${visibleShots.length} shot${visibleShots.length !== 1 ? 's' : ''}`
      : undefined;
  const emptyMessage = isPendingView
    ? 'No pending activities'
    : `No shots in ${titleCase(stageLabel(stageFilter))}`;

  const reasonFor = (stage: string): string => {
    switch (stage) {
      case 'DAILIES':
        return 'Has dailies but missing edit export';
      case 'EDIT_EXPORT':
        return 'Ready for turnover';
      case 'CAPTURE':
        return 'Captured, awaiting camera master';
      case 'CAMERA_MASTER':
        return 'Camera master ready, awaiting dailies';
      case 'TURNOVER':
        return 'Turned over, awaiting archive';
      case 'ARCHIVE':
        return 'Archived';
      default:
        return '-';
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>

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
        <>
          <CardSection title="Shots by Stage">
            <div className="stage-grid">
              <StagePill
                stage={ALL}
                label="All Pending"
                count={blockedShots.length}
                selected={stageFilter === ALL}
                onClick={() => setStageFilter(ALL)}
              />
              {displayStages.map((stage) => (
                <StagePill
                  key={stage}
                  stage={stage}
                  count={stageCounts[stage] || 0}
                  selected={stageFilter === stage}
                  onClick={() => setStageFilter(stage)}
                />
              ))}
            </div>
          </CardSection>

          <CardSection title={listTitle} subtitle={listSubtitle} accent={stageFilter}>
            {visibleShots.length > 0 ? (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Description</th>
                      <th>Shot Code</th>
                      <th>Scene</th>
                      <th>Stage</th>
                      <th>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleShots.map((shot) => (
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
                        <td>{reasonFor(shot.stage)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">{emptyMessage}</div>
            )}
          </CardSection>
        </>
      )}
    </div>
  );
}
