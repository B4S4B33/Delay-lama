import React, { useState, useEffect } from 'react';
import { API_URL } from '../constants/config';
import { formatPercent } from '../utils/formatting';

function ModelInfo() {
  const [metadata, setMetadata] = useState(null);
  const [featureImportance, setFeatureImportance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchModelInfo() {
      try {
        const [metaRes, fiRes] = await Promise.all([
          fetch(`${API_URL}/metadata`),
          fetch(`${API_URL}/feature-importance`),
        ]);
        
        if (metaRes.ok) {
          setMetadata(await metaRes.json());
        }
        
        if (fiRes.ok) {
          const fiData = await fiRes.json();
          setFeatureImportance(fiData.features || []);
        }
      } catch (err) {
        setError('Failed to load model information. Is the backend running?');
      } finally {
        setLoading(false);
      }
    }
    
    fetchModelInfo();
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="loading-container">
          <div className="spinner"></div>
          <span className="loading-text">Loading model info...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-banner">
          <span>⚠️</span> {error}
        </div>
      </div>
    );
  }

  const maxImportance = featureImportance.length > 0
    ? Math.max(...featureImportance.map((f) => f.importance))
    : 1;

  return (
    <div className="card">
      <h2 className="card-header">
        <span>📊</span> Model Information
      </h2>

      {metadata && (
        <>
          {/* Performance Metrics */}
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>
            Performance Metrics
          </h3>
          
          <div className="model-info-grid">
            <div className="metric-card">
              <div className="metric-value">{formatPercent(metadata.roc_auc)}</div>
              <div className="metric-label">ROC-AUC</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{formatPercent(metadata.accuracy)}</div>
              <div className="metric-label">Accuracy</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{formatPercent(metadata.precision)}</div>
              <div className="metric-label">Precision</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{formatPercent(metadata.recall)}</div>
              <div className="metric-label">Recall</div>
            </div>
          </div>

          {/* Model Details */}
          <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: 'var(--bg-tertiary)', borderRadius: '8px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.875rem' }}>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Version: </span>
                <strong>{metadata.model_version}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Training Data: </span>
                <strong>{metadata.training_data_range}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Features: </span>
                <strong>{metadata.total_features}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Target: </span>
                <strong>ArrDel15 (≥15 min delay)</strong>
              </div>
            </div>
          </div>

          {/* Confusion Matrix */}
          {metadata.confusion_matrix && Object.keys(metadata.confusion_matrix).length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>
                Confusion Matrix
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr 1fr', gap: '0', fontSize: '0.875rem', maxWidth: '400px' }}>
                <div></div>
                <div style={{ textAlign: 'center', fontWeight: 600, padding: '0.5rem', color: 'var(--text-secondary)' }}>Predicted On-Time</div>
                <div style={{ textAlign: 'center', fontWeight: 600, padding: '0.5rem', color: 'var(--text-secondary)' }}>Predicted Delayed</div>
                
                <div style={{ fontWeight: 600, padding: '0.5rem', color: 'var(--text-secondary)' }}>Actual On-Time</div>
                <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: 'var(--success-bg)', borderRadius: '4px', fontWeight: 600 }}>
                  {metadata.confusion_matrix.tn || 0}
                </div>
                <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: 'var(--warning-bg)', borderRadius: '4px', fontWeight: 600 }}>
                  {metadata.confusion_matrix.fp || 0}
                </div>
                
                <div style={{ fontWeight: 600, padding: '0.5rem', color: 'var(--text-secondary)' }}>Actual Delayed</div>
                <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: 'var(--warning-bg)', borderRadius: '4px', fontWeight: 600 }}>
                  {metadata.confusion_matrix.fn || 0}
                </div>
                <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: 'var(--success-bg)', borderRadius: '4px', fontWeight: 600 }}>
                  {metadata.confusion_matrix.tp || 0}
                </div>
              </div>
            </div>
          )}

          {/* Feature Importance */}
          {featureImportance.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>
                Feature Importance (Global)
              </h3>
              
              {featureImportance.map((feature) => (
                <div key={feature.name} className="feature-bar-container">
                  <div className="feature-bar-label">
                    <span className="feature-bar-name">{feature.name}</span>
                    <span className="feature-bar-score">
                      {(feature.importance * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="feature-bar-track">
                    <div
                      className="feature-bar-fill"
                      style={{
                        width: `${(feature.importance / maxImportance) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Feature List */}
          <div style={{ marginTop: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
              Input Features
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {metadata.feature_list.map((feature) => (
                <span
                  key={feature}
                  style={{
                    padding: '0.375rem 0.75rem',
                    backgroundColor: 'var(--bg-tertiary)',
                    borderRadius: '6px',
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                  }}
                >
                  {feature}
                </span>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ModelInfo;
