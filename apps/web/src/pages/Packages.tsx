import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Package } from '../api/client';

export function PackagesPage() {
  const [packages, setPackages] = useState<Package[]>([]);
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [packageMembers, setPackageMembers] = useState<Array<{ version_id: string; version_type: string; storage_uri: string }>>([]);
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
    <div style={{ padding: '24px', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ marginBottom: '16px' }}>
        <a href="/" style={{ color: '#0066cc' }}>← Back to Dashboard</a>
      </div>

      <h1>Packages</h1>

      {error && (
        <div style={{ padding: '12px', background: '#fee', border: '1px solid #fcc', marginBottom: '16px' }}>
          Error: {error}
        </div>
      )}

      {loading && <div>Loading...</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div>
          <h2>Package List</h2>
          {packages.length > 0 ? (
            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr style={{ background: '#f0f0f0' }}>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Label</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Vendor</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Created</th>
                </tr>
              </thead>
              <tbody>
                {packages.map(pkg => (
                  <tr
                    key={pkg.id}
                    onClick={() => setSelectedPackage(pkg.id)}
                    style={{
                      cursor: 'pointer',
                      background: selectedPackage === pkg.id ? '#e6f3ff' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{pkg.package_type}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{pkg.label}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{pkg.vendor || '-'}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                      {new Date(pkg.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No packages found</p>
          )}
        </div>

        <div>
          <h2>Package Members</h2>
          {selectedPackage && packageMembers.length > 0 ? (
            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr style={{ background: '#f0f0f0' }}>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Version Type</th>
                  <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Storage URI</th>
                </tr>
              </thead>
              <tbody>
                {packageMembers.map(member => (
                  <tr key={member.version_id}>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>{member.version_type}</td>
                    <td style={{ padding: '8px', border: '1px solid #ddd', fontFamily: 'monospace', fontSize: '12px' }}>
                      {member.storage_uri}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : selectedPackage ? (
            <p>No members in this package</p>
          ) : (
            <p>Select a package to view members</p>
          )}
        </div>
      </div>
    </div>
  );
}
