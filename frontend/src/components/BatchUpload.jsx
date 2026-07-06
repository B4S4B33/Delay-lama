import React, { useState, useRef } from 'react';
import { apiUpload, apiGet } from '../utils/api';
import { API_URL } from '../constants/config';

const ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls'];

function isAllowedFile(filename) {
  const ext = '.' + filename.split('.').pop().toLowerCase();
  return ALLOWED_EXTENSIONS.includes(ext);
}

function BatchUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (isAllowedFile(droppedFile.name)) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Only CSV and Excel files (.csv, .xlsx, .xls) are allowed');
      }
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (isAllowedFile(selectedFile.name)) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Only CSV and Excel files (.csv, .xlsx, .xls) are allowed');
        e.target.value = '';
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV or Excel file');
      return;
    }
    
    setUploading(true);
    setError(null);
    setResults(null);
    
    try {
      const result = await apiUpload('/predict-batch', file);
      setResults(result);
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getFileIcon = (filename) => {
    if (!filename) return '📁';
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'csv') return '📄';
    if (ext === 'xlsx' || ext === 'xls') return '📊';
    return '📁';
  };

  return (
    <div className="card">
      <h2 className="card-header">
        <span>📋</span> Batch Prediction
      </h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
        Upload a CSV or Excel file with multiple flights for batch delay prediction.
      </p>

      {/* Expected format info */}
      <div style={{
        padding: '1rem',
        backgroundColor: 'var(--bg-tertiary)',
        borderRadius: '8px',
        marginBottom: '1.5rem',
        fontSize: '0.8125rem',
      }}>
        <strong>Supported formats:</strong>
        <code style={{ marginLeft: '0.5rem', color: 'var(--accent-color)' }}>
          .csv, .xlsx, .xls
        </code>
        <div style={{ marginTop: '0.5rem' }}>
          <strong>Required columns:</strong>
          <code style={{ marginLeft: '0.5rem', color: 'var(--accent-color)' }}>
            airline, origin, dest, flight_date, scheduled_dep_time, distance (optional)
          </code>
        </div>
        <div style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
          Example: <code>Delta Air Lines Inc., ATL, LAX, 2024-06-15, 08:30, 1946</code>
        </div>
      </div>

      {/* Drop zone */}
      <div
        className={`file-upload-zone ${dragActive ? 'file-upload-zone--active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="file-upload-icon">{getFileIcon(file?.name)}</div>
        <div className="file-upload-text">
          {file ? (
            <span>
              <strong>{file.name}</strong> ({(file.size / 1024).toFixed(1)} KB)
            </span>
          ) : (
            <>
              Drag & drop a CSV or Excel file here, or click to browse
              <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Accepts .csv, .xlsx, .xls files up to 10MB
              </div>
            </>
          )}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {/* Buttons */}
      <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
        <button className="btn btn-secondary" onClick={handleReset} disabled={uploading}>
          Reset
        </button>
        <button className="btn btn-primary" onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? '⏳ Processing...' : '🚀 Process Batch'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="error-banner" style={{ marginTop: '1rem' }}>
          <span>⚠️</span> {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="batch-status fade-in" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
            ✅ Batch Complete
          </h3>
          
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            {results.message}
          </p>

          <div className="batch-stats">
            <div className="batch-stat">
              <div className="batch-stat-value">{results.batch_id ? '✓' : '—'}</div>
              <div className="batch-stat-label">Batch ID</div>
            </div>
            <div className="batch-stat">
              <div className="batch-stat-value" style={{ color: 'var(--danger-color)' }}>
                {results.message.match(/(\d+) delayed/)?.[1] || '0'}
              </div>
              <div className="batch-stat-label">Delayed</div>
            </div>
            <div className="batch-stat">
              <div className="batch-stat-value" style={{ color: 'var(--success-color)' }}>
                {results.message.match(/(\d+) on-time/)?.[1] || '0'}
              </div>
              <div className="batch-stat-label">On-Time</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BatchUpload;
