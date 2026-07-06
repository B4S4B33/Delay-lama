import React, { useState, useEffect, createContext } from 'react';
import Header from './components/Header';
import PredictionForm from './components/PredictionForm';
import PredictionResult from './components/PredictionResult';
import ExplainabilityPanel from './components/ExplainabilityPanel';
import HistoricalRouteStats from './components/HistoricalRouteStats';
import AirlineComparison from './components/AirlineComparison';
import BatchUpload from './components/BatchUpload';
import ModelInfo from './components/ModelInfo';
import ScopeDisclaimer from './components/ScopeDisclaimer';
import LoadingSpinner from './components/LoadingSpinner';

export const ThemeContext = createContext();

function App() {
  const [isDark, setIsDark] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [routeStats, setRouteStats] = useState(null);
  const [activeTab, setActiveTab] = useState('predict'); // 'predict' | 'compare' | 'batch' | 'model'
  const [error, setError] = useState(null);

  // Restore theme from session storage
  useEffect(() => {
    const stored = sessionStorage.getItem('theme');
    if (stored) {
      const dark = JSON.parse(stored);
      setIsDark(dark);
      document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    sessionStorage.setItem('theme', JSON.stringify(newTheme));
    document.documentElement.setAttribute('data-theme', newTheme ? 'dark' : 'light');
  };

  const handlePredict = (result) => {
    setPrediction(result);
    setError(null);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  const handleRouteStats = (stats) => {
    setRouteStats(stats);
  };

  const handleError = (errMsg) => {
    setError(errMsg);
    setPrediction(null);
  };

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      <div data-theme={isDark ? 'dark' : 'light'} className="app-container">
        <Header activeTab={activeTab} onTabChange={setActiveTab} />
        <ScopeDisclaimer />
        
        <main className="main-content">
          {/* ─── Predict Tab ─── */}
          {activeTab === 'predict' && (
            <div className="predict-layout">
              <div className="predict-main">
                <PredictionForm 
                  onPredict={handlePredict}
                  onLoading={handleLoading}
                  onRouteStats={handleRouteStats}
                  onError={handleError}
                />
                
                {loading && <LoadingSpinner />}
                
                {error && (
                  <div className="error-banner card">
                    <span className="error-icon">⚠️</span>
                    <span>{error}</span>
                  </div>
                )}
                
                {prediction && (
                  <>
                    <PredictionResult prediction={prediction} />
                    <ExplainabilityPanel factors={prediction.top_factors} />
                  </>
                )}
              </div>
              
              {routeStats && (
                <aside className="predict-sidebar">
                  <HistoricalRouteStats stats={routeStats} />
                </aside>
              )}
            </div>
          )}
          
          {/* ─── Compare Tab ─── */}
          {activeTab === 'compare' && (
            <AirlineComparison />
          )}
          
          {/* ─── Batch Tab ─── */}
          {activeTab === 'batch' && (
            <BatchUpload />
          )}
          
          {/* ─── Model Info Tab ─── */}
          {activeTab === 'model' && (
            <ModelInfo />
          )}
        </main>
      </div>
    </ThemeContext.Provider>
  );
}

export default App;
