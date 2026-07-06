import React from 'react';

function LoadingSpinner({ message = 'Processing prediction...' }) {
  return (
    <div className="loading-container">
      <div className="spinner" aria-label="Loading"></div>
      <span className="loading-text">{message}</span>
    </div>
  );
}

export default LoadingSpinner;
