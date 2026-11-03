import React from 'react';
import { NavLink } from 'react-router-dom';
import { Search, BarChart3, LineChart, Info, Stethoscope, Database } from 'lucide-react';

export default function Sidebar({ isOpen, onClose }) {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <Stethoscope size={22} />
        </div>
        <div className="sidebar-title-group">
          <h1>MediRetrieve</h1>
          <span>NFCorpus Research</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <Search size={18} />
          <span>Literature Search</span>
        </NavLink>

        <NavLink
          to="/comparison"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <BarChart3 size={18} />
          <span>Model Comparison</span>
        </NavLink>

        <NavLink
          to="/evaluation"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <LineChart size={18} />
          <span>Precision-Recall</span>
        </NavLink>

        <NavLink
          to="/about"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <Info size={18} />
          <span>Methodology & About</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="dataset-badge">
          <Database size={13} />
          <span>NFCorpus Benchmark</span>
        </div>
        <p style={{ marginTop: '0.5rem' }}>Medical IR Analytics v1.0</p>
      </div>
    </aside>
  );
}
