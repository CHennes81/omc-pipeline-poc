import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { ShotDetailPage } from './pages/ShotDetail';
import { PackagesPage } from './pages/Packages';
import { AskPage } from './pages/Ask';
import { AboutDialog } from './components/AboutDialog';
import { BuildFooter } from './components/BuildFooter';

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <nav
          style={{
            background: '#f0f0f0',
            padding: '12px 24px',
            borderBottom: '1px solid #ddd',
            display: 'flex',
            gap: '24px',
            alignItems: 'center',
          }}
        >
          <Link to="/" style={{ textDecoration: 'none', color: '#333', fontWeight: 'bold' }}>
            Production Lineage Concierge
          </Link>
          <Link to="/" style={{ textDecoration: 'none', color: '#666' }}>
            Dashboard
          </Link>
          <Link to="/packages" style={{ textDecoration: 'none', color: '#666' }}>
            Packages
          </Link>
          <Link to="/ask" style={{ textDecoration: 'none', color: '#666' }}>
            Ask
          </Link>
          <div style={{ marginLeft: 'auto' }}>
            <AboutDialog />
          </div>
        </nav>

        <main style={{ flex: 1, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Arial' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/shot/:shotCode" element={<ShotDetailPage />} />
            <Route path="/packages" element={<PackagesPage />} />
            <Route path="/ask" element={<AskPage />} />
          </Routes>
        </main>

        <BuildFooter />
      </div>
    </BrowserRouter>
  );
}
