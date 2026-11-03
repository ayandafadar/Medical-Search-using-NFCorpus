import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { fetchHealth } from '../../services/api';

export default function AppLayout({ title, description, children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const data = await fetchHealth();
        if (isMounted) setHealth(data);
      } catch (err) {
        if (isMounted) setHealth({ status: 'unhealthy', initialized: false });
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="app-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="main-wrapper">
        <Header
          title={title}
          description={description}
          health={health}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
        <main className="page-container">
          {children}
        </main>
      </div>
    </div>
  );
}
