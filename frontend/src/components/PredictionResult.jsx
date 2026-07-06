import React from 'react';
import { formatProbability } from '../utils/formatting';

function PredictionResult({ prediction }) {
  if (!prediction) return null;

  const { predicted_delayed, delay_probability, confidence } = prediction;
  const prob = (delay_probability * 100).toFixed(1);
  const isDelayed = predicted_delayed;

  // Color for the probability bar
  const barColor = isDelayed ? 'var(--bar-high)' : 'var(--bar-low)';
  if (delay_probability > 0.4 && delay_probability < 0.7) {
    // Use warning color for uncertain range
  }

  return (
    <div className="card prediction-result fade-in" style={{ marginTop: '1.5rem' }}>
      {/* Header */}
      <div className="result-header">
        <div className={`result-label result-label--${isDelayed ? 'delayed' : 'on-time'}`}>
          <span style={{ fontSize: '1.75rem' }}>
            {isDelayed ? '⚠️' : '✅'}
          </span>
          <span>{isDelayed ? 'Likely Delayed' : 'Likely On-Time'}</span>
        </div>
        <div className="result-probability" style={{ color: barColor }}>
          {prob}%
        </div>
      </div>

      {/* Probability Bar */}
      <div className="probability-bar-container">
        <div className="probability-bar-track">
          <div
            className="probability-bar-fill"
            style={{
              width: `${delay_probability * 100}%`,
              backgroundColor: barColor,
            }}
            role="progressbar"
            aria-valuenow={delay_probability}
            aria-valuemin={0}
            aria-valuemax={1}
            aria-label={`Delay probability: ${prob}%`}
          />
        </div>
        <div className="probability-bar-labels">
          <span>0% — On-Time</span>
          <span>50%</span>
          <span>100% — Delayed</span>
        </div>
      </div>

      {/* Meta info */}
      <div className="result-meta">
        <div className={`status-badge status-badge--${isDelayed ? 'delayed' : 'on-time'}`}>
          {isDelayed ? '⚠️ Delay' : '✅ On-Time'}
        </div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          Confidence: <strong>{confidence}</strong>
        </div>
      </div>
    </div>
  );
}

export default PredictionResult;
