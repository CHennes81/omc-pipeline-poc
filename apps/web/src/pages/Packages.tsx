import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Package } from '../api/client';
import './PageStyles.css';

export function PackagesPage() {
  const [packages, setPackages] = useState<Package[]>([]);
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [packageMembers, setPackageMembers] = useState<
    Array<{ version_id: string; version_type: string; storage_uri: string }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const productionCode = 'EXFTR'; // TODO: get from context

  useEffect(() => {
    loadPackages();
  }, []);

  useEffect(() => {
    if (selectedPackage) {
      loadPackageDetail(selectedPackage);
    }
  }, [selectedPackage]);

  const loadPackages = async () => {
    try {
      setLoading(true);
      const data = await api.getPackages(productionCode);
      setPackages(data.packages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load packages');
    } finally {
      setLoading(false);
    }
  };

  const loadPackageDetail = async (packageId: string) => {
    try {
      setLoading(true);
      const data = await api.getPackageDetail(packageId);
      setPackageMembers(data.members);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load package details');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div style={{ marginBottom: '16px' }}>
        <a href="/" className="page-back-link">
          ← Back to Dashboard
        </a>
      </div>

      <h1 className="page-title">Packages</h1>

      {error && <div className="page-error">Error: {error}</div>}

      {loading && <div className="page-loading">Loading...</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div>
          <h2 className="page-section">Package List</h2>
          {packages.length > 0 ? (
            <table className="page-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Label</th>
                  <th>Vendor</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {packages.map((pkg) => (
                  <tr
                    key={pkg.id}
                    onClick={() => setSelectedPackage(pkg.id)}
                    className={selectedPackage === pkg.id ? 'page-list-item-selected' : ''}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>{pkg.package_type}</td>
                    <td>{pkg.label}</td>
                    <td>{pkg.vendor || '-'}</td>
                    <td>{new Date(pkg.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="page-empty">No packages found</p>
          )}
        </div>

        <div>
          <h2 className="page-section">Package Members</h2>
          {selectedPackage && packageMembers.length > 0 ? (
            <table className="page-table">
              <thead>
                <tr>
                  <th>Version Type</th>
                  <th>Storage URI</th>
                </tr>
              </thead>
              <tbody>
                {packageMembers.map((member) => (
                  <tr key={member.version_id}>
                    <td>{member.version_type}</td>
                    <td className="monospace">{member.storage_uri}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : selectedPackage ? (
            <p className="page-empty">No members in this package</p>
          ) : (
            <p className="page-empty">Select a package to view members</p>
          )}
        </div>
      </div>
    </div>
  );
}
