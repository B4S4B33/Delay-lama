import React, { useState } from 'react';
import { API_URL } from '../constants/config';
import { formatProbability } from '../utils/formatting';

function AirlineComparison() {
  const [origin, setOrigin] = useState('');
  const [dest, setDest] = useState('');
  const [flightDate, setFlightDate] = useState('');
  const [depTime, setDepTime] = useState('');
  const [comparisons, setComparisons] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const AIRPORTS = [
    'ATL', 'AUS', 'BNA', 'BOS', 'BWI', 'CLE', 'CLT', 'CVG', 'DCA',
    'DEN', 'DFW', 'DTW', 'EWR', 'FLL', 'HNL', 'HOU', 'IAD', 'IAH',
    'JFK', 'LAS', 'LAX', 'LGA', 'MCI', 'MCO', 'MDW', 'MEM', 'MIA',
    'MKE', 'MSP', 'MSY', 'OAK', 'ONT', 'ORD', 'PHL', 'PHX', 'PIT',
    'RDU', 'SAN', 'SAT', 'SEA', 'SFO', 'SLC', 'SMF', 'SNA', 'STL',
    'TPA', 'TUS',
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!origin || !dest || !flightDate || !depTime) {
      setError('Please fill in all fields');
      return;
    }
    
    if (origin === dest) {
      setError('Origin and destination must be different');
      return;
    }
    
    setLoading(true);
    setError(null);
    setComparisons(null);
    
    try {
      const response = await fetch(`${API_URL}/compare-airlines`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: origin.toUpperCase(),
          dest: dest.toUpperCase(),
          flight_date: flightDate,
          scheduled_dep_time: depTime,
        }),
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Comparison failed');
      }
      
      const result = await response.json();
      setComparisons(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="card">
      <h2 className="card-header">
        <span>⚖️</span> Compare Airlines
      </h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
        Compare predicted delay risk across airlines for the same route and time.
      </p>

      <form onSubmit={handleSubmit} className="prediction-form">
        <div className="form-group">
          <label className="form-label" htmlFor="cmp-origin">Origin</label>
          <select id="cmp-origin" className="form-select" value={origin} onChange={(e) => setOrigin(e.target.value)} required>
            <option value="">Select origin...</option>
            {AIRPORTS.map((code) => <option key={code} value={code}>{code}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="cmp-dest">Destination</label>
          <select id="cmp-dest" className="form-select" value={dest} onChange={(e) => setDest(e.target.value)} required>
            <option value="">Select destination...</option>
            {AIRPORTS.map((code) => <option key={code} value={code}>{code}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="cmp-date">Flight Date</label>
          <input type="date" id="cmp-date" className="form-input" value={flightDate} onChange={(e) => setFlightDate(e.target.value)} min={today} required />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="cmp-time">Departure Time</label>
          <input type="time" id="cmp-time" className="form-input" value={depTime} onChange={(e) => setDepTime(e.target.value)} required />
        </div>

        <div className="form-submit-row">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '⏳ Comparing...' : '⚖️ Compare Airlines'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-banner" style={{ marginTop: '1rem' }}>
          <span>⚠️</span> {error}
        </div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <span className="loading-text">Comparing airlines...</span>
        </div>
      )}

      {comparisons && comparisons.comparisons && (
        <div className="fade-in" style={{ marginTop: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>
            {comparisons.route} — Delay Risk by Airline
          </h3>

          <div className="comparison-grid">
            {comparisons.comparisons.map((item, index) => {
              const prob = (item.delay_probability * 100).toFixed(1);
              const isDelayed = item.predicted_delayed;
              const barColor = isDelayed ? 'var(--bar-high)' : 'var(--bar-low)';
              
              return (
                <div key={item.airline} className="card comparison-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div className="comparison-airline">
                        {index === 0 && <span style={{ marginRight: '0.375rem' }}>🏆</span>}
                        {item.airline_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.airline}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="comparison-prob" style={{ color: barColor }}>
                        {prob}%
                      </div>
                      <div className={`status-badge status-badge--${isDelayed ? 'delayed' : 'on-time'}`} style={{ fontSize: '0.75rem' }}>
                        {isDelayed ? '⚠️ Delayed' : '✅ On-Time'}
                      </div>
                    </div>
                  </div>
                  
                  {/* Mini bar */}
                  <div style={{ marginTop: '0.75rem' }}>
                    <div className="probability-bar-track" style={{ height: '6px' }}>
                      <div
                        className="probability-bar-fill"
                        style={{
                          width: `${item.delay_probability * 100}%`,
                          backgroundColor: barColor,
                        }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {comparisons.comparisons.length === 0 && (
            <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
              No comparison data available for this route.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default AirlineComparison;
