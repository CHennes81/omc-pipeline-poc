import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { ShotDetailPage } from './pages/ShotDetail';
import { PackagesPage } from './pages/Packages';
import { AskPage } from './pages/Ask';
import { AllShots } from './pages/AllShots';
import { AboutDialog } from './components/AboutDialog';
import { BuildFooter } from './components/BuildFooter';

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <nav
          style={{
            background: 'var(--nav-bg)',
            padding: '12px 24px',
            borderBottom: '1px solid var(--nav-border)',
            display: 'flex',
            gap: '24px',
            alignItems: 'center',
          }}
        >
          <Link
            to="/"
            style={{ textDecoration: 'none', color: 'var(--nav-link-active)', fontWeight: 'bold' }}
          >
            Production Lineage Concierge
          </Link>
          <Link to="/" style={{ textDecoration: 'none', color: 'var(--nav-link)' }}>
            Dashboard
          </Link>
          <Link to="/packages" style={{ textDecoration: 'none', color: 'var(--nav-link)' }}>
            Packages
          </Link>
          <Link to="/ask" style={{ textDecoration: 'none', color: 'var(--nav-link)' }}>
            Ask
          </Link>
          <Link to="/shots" style={{ textDecoration: 'none', color: 'var(--nav-link)' }}>
            All Shots
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
            <Route path="/shots" element={<AllShots />} />
          </Routes>
        </main>

        <BuildFooter />
      </div>
    </BrowserRouter>
  );
}
