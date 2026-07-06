import React from 'react';
import { featureLabel } from '../utils/formatting';

function ExplainabilityPanel({ factors }) {
  if (!factors || factors.length === 0) return null;

  return (
    <div className="card explainability-panel fade-in" style={{ marginTop: '1.5rem' }}>
      <h3 className="explainability-title">
        <span>🔍</span> Why This Prediction?
      </h3>
      <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
        These factors most influenced the model's decision for this flight:
      </p>

      <ul className="factor-list">
        {factors.map((factor, index) => (
          <li key={factor.feature} className="factor-item">
            <div>
              <span className="factor-name">
                {index + 1}. {featureLabel(factor.feature)}
              </span>
              <span style={{
                marginLeft: '0.5rem',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
              }}>
                ({(factor.impact * 100).toFixed(1)}% influence)
              </span>
            </div>
            <span className={`factor-direction factor-direction--${factor.direction}`}>
              {factor.direction === 'increases' && '📈 Increases risk'}
              {factor.direction === 'decreases' && '📉 Decreases risk'}
              {factor.direction === 'influences' && '🔄 Influences'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ExplainabilityPanel;
