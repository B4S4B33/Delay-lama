import React, { useState, useEffect } from 'react';
import { API_URL } from '../constants/config';

const DEFAULT_AIRLINES = [
  'Alaska Airlines', 'Allegiant Air', 'American Airlines',
  'Delta Air Lines', 'Endeavor Air', 'Envoy Air',
  'Frontier Airlines', 'Hawaiian Airlines', 'JetBlue Airways',
  'Mesa Airlines', 'PSA Airlines', 'Republic Airways',
  'SkyWest Airlines', 'Southwest Airlines', 'Spirit Airlines',
  'United Airlines',
];

const DEFAULT_AIRPORTS = [
  'ATL', 'AUS', 'BNA', 'BOS', 'BWI', 'CLE', 'CLT', 'CVG', 'DCA',
  'DEN', 'DFW', 'DTW', 'EWR', 'FLL', 'HNL', 'HOU', 'IAD', 'IAH',
  'JFK', 'LAS', 'LAX', 'LGA', 'MCI', 'MCO', 'MDW', 'MEM', 'MIA',
  'MKE', 'MSP', 'MSY', 'OAK', 'ONT', 'ORD', 'PHL', 'PHX', 'PIT',
  'RDU', 'SAN', 'SAT', 'SEA', 'SFO', 'SLC', 'SMF', 'SNA', 'STL',
  'TPA', 'TUS',
];

function PredictionForm({ onPredict, onLoading, onRouteStats, onError }) {
  const [airlines, setAirlines] = useState(DEFAULT_AIRLINES);
  const [airports, setAirlinesCode] = useState(DEFAULT_AIRPORTS);

  const [airline, setAirline] = useState('');
  const [origin, setOrigin] = useState('');
  const [dest, setDest] = useState('');
  const [flightDate, setFlightDate] = useState('');
  const [depTime, setDepTime] = useState('');
  const [distance, setDistance] = useState('');

  const [submitting, setSubmitting] = useState(false);

  // Fetch airlines and airports from API on mount
  useEffect(() => {
    async function fetchOptions() {
      try {
        const [airlinesRes, airportsRes] = await Promise.all([
          fetch(`${API_URL}/airlines`),
          fetch(`${API_URL}/airports`),
        ]);
        
        if (airlinesRes.ok) {
          const data = await airlinesRes.json();
          if (data.airlines && data.airlines.length > 0) {
            setAirlines(data.airlines.map((a) => a.name));
          }
        }
        
        if (airportsRes.ok) {
          const data = await airportsRes.json();
          if (data.airports && data.airports.length > 0) {
            setAirlinesCode(data.airports.map((a) => a.code));
          }
        }
      } catch (err) {
        // Use defaults if API not available
        console.warn('Using default airline/airport lists');
      }
    }
    fetchOptions();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!airline || !origin || !dest || !flightDate || !depTime) {
      onError('Please fill in all required fields');
      return;
    }
    
    if (origin === dest) {
      onError('Origin and destination must be different');
      return;
    }
    
    setSubmitting(true);
    onLoading(true);
    onError(null);
    
    try {
      const requestBody = {
        airline,
        origin: origin.toUpperCase(),
        dest: dest.toUpperCase(),
        flight_date: flightDate,
        scheduled_dep_time: depTime,
      };
      
      if (distance) {
        requestBody.distance = parseInt(distance, 10);
      }
      
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Prediction failed (${response.status})`);
      }
      
      const result = await response.json();
      onPredict(result);
      
      // Set route stats if available
      if (result.route_historical_delay_rate !== null) {
        onRouteStats({
          origin: origin.toUpperCase(),
          dest: dest.toUpperCase(),
          historical_delay_rate: result.route_historical_delay_rate,
          sample_count: result.route_sample_count,
        });
      }
      
    } catch (err) {
      onError(err.message || 'An unexpected error occurred');
    } finally {
      setSubmitting(false);
      onLoading(false);
    }
  };

  const handleReset = () => {
    setAirline('');
    setOrigin('');
    setDest('');
    setFlightDate('');
    setDepTime('');
    setDistance('');
    onError(null);
  };

  // Set default date to today
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="card">
      <h2 className="card-header">
        <span>🔍</span> Flight Prediction
      </h2>
      
      <form onSubmit={handleSubmit} className="prediction-form">
        {/* Airline */}
        <div className="form-group">
          <label className="form-label" htmlFor="airline">Airline</label>
          <select
            id="airline"
            className="form-select"
            value={airline}
            onChange={(e) => setAirline(e.target.value)}
            required
          >
            <option value="">Select airline...</option>
            {airlines.map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>

        {/* Origin */}
        <div className="form-group">
          <label className="form-label" htmlFor="origin">Origin</label>
          <select
            id="origin"
            className="form-select"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            required
          >
            <option value="">Select origin...</option>
            {airports.map((code) => (
              <option key={code} value={code}>{code}</option>
            ))}
          </select>
        </div>

        {/* Destination */}
        <div className="form-group">
          <label className="form-label" htmlFor="dest">Destination</label>
          <select
            id="dest"
            className="form-select"
            value={dest}
            onChange={(e) => setDest(e.target.value)}
            required
          >
            <option value="">Select destination...</option>
            {airports.map((code) => (
              <option key={code} value={code}>{code}</option>
            ))}
          </select>
        </div>

        {/* Flight Date */}
        <div className="form-group">
          <label className="form-label" htmlFor="flightDate">Flight Date</label>
          <input
            type="date"
            id="flightDate"
            className="form-input"
            value={flightDate}
            onChange={(e) => setFlightDate(e.target.value)}
            min={today}
            required
          />
        </div>

        {/* Departure Time */}
        <div className="form-group">
          <label className="form-label" htmlFor="depTime">Departure Time</label>
          <input
            type="time"
            id="depTime"
            className="form-input"
            value={depTime}
            onChange={(e) => setDepTime(e.target.value)}
            required
          />
        </div>

        {/* Distance (optional) */}
        <div className="form-group">
          <label className="form-label" htmlFor="distance">Distance (miles, optional)</label>
          <input
            type="number"
            id="distance"
            className="form-input"
            value={distance}
            onChange={(e) => setDistance(e.target.value)}
            placeholder="Auto-estimated if empty"
            min="0"
          />
        </div>

        {/* Buttons */}
        <div className="form-submit-row">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleReset}
            disabled={submitting}
          >
            Reset
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? '⏳ Predicting...' : '🚀 Predict Delay'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default PredictionForm;
