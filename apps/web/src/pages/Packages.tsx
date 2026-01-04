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
      <h1 className="page-title">Packages</h1>

      {error && <div className="page-error">Error: {error}</div>}

      {loading && <div className="page-loading">Loading...</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div className="packages-section">
          <h2 className="packages-section-title">Package List</h2>
          <div className="packages-section-divider"></div>
          {packages.length > 0 ? (
            <table className="page-table">
              <thead>
                <tr>
                  <th>Label</th>
                  <th>Type</th>
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
                    <td>
                      <a
                        href="#"
                        className="packages-label-link"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setSelectedPackage(pkg.id);
                        }}
                      >
                        {pkg.label}
                      </a>
                    </td>
                    <td>{pkg.package_type}</td>
                    <td>{pkg.vendor || '-'}</td>
                    <td>{new Date(pkg.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="packages-empty-state">No packages found</p>
          )}
        </div>

        <div className="packages-section">
          <h2 className="packages-section-title">Package Members</h2>
          <div className="packages-section-divider"></div>
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
            <p className="packages-empty-state">No members in this package</p>
          ) : (
            <p className="packages-empty-state">Select a package to view members</p>
          )}
        </div>
      </div>
    </div>
  );
}
