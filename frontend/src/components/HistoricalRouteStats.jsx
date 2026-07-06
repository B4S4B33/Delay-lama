import React from 'react';
import { formatPercent, formatNumber } from '../utils/formatting';

function HistoricalRouteStats({ stats }) {
  if (!stats) return null;

  const { origin, dest, historical_delay_rate, sample_count } = stats;
  const delayRate = historical_delay_rate !== null ? historical_delay_rate : 0;
  const delayPercent = (delayRate * 100).toFixed(1);

  // Determine risk level
  let riskLevel, riskColor;
  if (delayRate < 0.15) {
    riskLevel = 'Low';
    riskColor = 'var(--success-color)';
  } else if (delayRate < 0.25) {
    riskLevel = 'Moderate';
    riskColor = 'var(--warning-color)';
  } else {
    riskLevel = 'High';
    riskColor = 'var(--danger-color)';
  }

  return (
    <div className="card route-stats">
      <div className="route-stats-header">
        <h3 className="route-stats-route">
          {origin} → {dest}
        </h3>
        <p className="route-stats-detail">Historical Route Statistics</p>
      </div>

      <div className="stat-item">
        <span className="stat-label">Delay Rate</span>
        <span className="stat-value" style={{ color: riskColor }}>
          {delayPercent}%
        </span>
      </div>

      <div className="stat-item">
        <span className="stat-label">Risk Level</span>
        <span className="stat-value" style={{ color: riskColor }}>
          {riskLevel}
        </span>
      </div>

      <div className="stat-item">
        <span className="stat-label">Sample Size</span>
        <span className="stat-value">
          {sample_count ? formatNumber(sample_count) : 'N/A'}
        </span>
      </div>

      <div className="stat-item">
        <span className="stat-label">On-Time Rate</span>
        <span className="stat-value">
          {((1 - delayRate) * 100).toFixed(1)}%
        </span>
      </div>

      {/* Disclaimer */}
      <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        backgroundColor: 'var(--bg-tertiary)',
        borderRadius: '6px',
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        lineHeight: '1.5',
      }}>
        ℹ️ Based on historical training data (2018-2022). Actual delays may vary due to weather, air traffic, and other real-time factors.
      </div>
    </div>
  );
}

export default HistoricalRouteStats;
