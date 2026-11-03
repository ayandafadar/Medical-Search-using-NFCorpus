import React from 'react';
import { Menu, Server, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export default function Header({ title, description, health, onToggleSidebar }) {
  const isHealthy = health && health.status === 'healthy';
  const docCount = health?.document_count || 3633;

  return (
    <header className="app-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button className="mobile-toggle" onClick={onToggleSidebar} aria-label="Toggle navigation">
          <Menu size={20} />
        </button>
        <div className="header-title-group">
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
      </div>

      <div className="header-right">
        <div className="dataset-badge">
          <Server size={13} />
          <span>{docCount.toLocaleString()} Documents</span>
        </div>

        <div className={`status-badge ${isHealthy ? 'healthy' : 'unhealthy'}`}>
          <span className="status-dot"></span>
          <span>{isHealthy ? 'Backend Ready' : 'Backend Offline'}</span>
        </div>
      </div>
    </header>
  );
}
