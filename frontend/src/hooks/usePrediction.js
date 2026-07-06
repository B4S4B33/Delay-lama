import { useState, useCallback } from 'react';
import { API_URL } from '../constants/config';

/**
 * Hook for making prediction API calls.
 * 
 * @returns {Object} Prediction state and methods
 */
export function usePrediction() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const predict = useCallback(async (requestData) => {
    setLoading(true);
    setError(null);
    setPrediction(null);
    
    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Prediction failed (${response.status})`);
      }
      
      const data = await response.json();
      setPrediction(data);
      return data;
      
    } catch (err) {
      const message = err.message || 'An unexpected error occurred';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setPrediction(null);
    setError(null);
    setLoading(false);
  }, []);

  return { prediction, loading, error, predict, reset };
}
