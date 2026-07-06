// API Configuration
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL || '';
export const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

// Model Constants
export const MODEL_VERSION = '1.0';
export const CONFIDENCE_THRESHOLDS = {
  high: { min: 0.8, max: 1.0 },
  moderate: { min: 0.4, max: 0.6 },
};

// Feature names for display
export const FEATURE_LABELS = {
  'Month': 'Month of Year',
  'DayofMonth': 'Day of Month',
  'DayOfWeek': 'Day of Week',
  'Airline': 'Airline',
  'Origin': 'Origin Airport',
  'Dest': 'Destination Airport',
  'Distance': 'Route Distance',
  'DepHour': 'Departure Hour',
  'ArrHour': 'Arrival Hour',
};
