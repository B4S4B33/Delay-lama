import React, { useContext } from 'react';
import { ThemeContext } from '../App';

const TABS = [
  { id: 'predict', label: 'Predict', icon: '✈️' },
  { id: 'compare', label: 'Compare', icon: '⚖️' },
  { id: 'batch', label: 'Batch', icon: '📋' },
  { id: 'model', label: 'Model Info', icon: '📊' },
];

function Header({ activeTab, onTabChange }) {
  const { isDark, toggleTheme } = useContext(ThemeContext);

  return (
    <header className="header">
      <div className="header-inner">
        {/* Brand */}
        <div className="header-brand">
          <span className="header-logo">✈️</span>
          <div>
            <div className="header-title">Flight Delay Predictor</div>
            <div className="header-subtitle">ML-Powered US Domestic Flights</div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="tabs" style={{ borderBottom: 'none', margin: 0 }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'tab--active' : ''}`}
              onClick={() => onTabChange(tab.id)}
              aria-current={activeTab === tab.id ? 'page' : undefined}
            >
              <span style={{ marginRight: '0.375rem' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Theme Toggle */}
        <div className="header-actions">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
          >
            <span className="theme-toggle-icon">
              {isDark ? '☀️' : '🌙'}
            </span>
            <span>{isDark ? 'Light' : 'Dark'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
