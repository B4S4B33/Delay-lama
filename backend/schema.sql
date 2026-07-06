-- ============================================================
-- US Flight Delay Predictor — Supabase Database Schema
-- Version: 1.0
-- ============================================================

-- ─── TABLES ────────────────────────────────────────────────

-- Airlines reference table
CREATE TABLE IF NOT EXISTS airlines (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Airports reference table
CREATE TABLE IF NOT EXISTS airports (
  id SERIAL PRIMARY KEY,
  code VARCHAR(3) UNIQUE NOT NULL,
  name VARCHAR(150) NOT NULL,
  city VARCHAR(100),
  state VARCHAR(2),
  latitude DECIMAL(8, 6),
  longitude DECIMAL(9, 6),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Routes with historical delay statistics
CREATE TABLE IF NOT EXISTS routes (
  id SERIAL PRIMARY KEY,
  origin_id INT REFERENCES airports(id) ON DELETE CASCADE,
  dest_id INT REFERENCES airports(id) ON DELETE CASCADE,
  distance_miles INT,
  historical_delay_rate DECIMAL(5, 4),
  sample_count INT,
  last_updated TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(origin_id, dest_id)
);

CREATE INDEX IF NOT EXISTS idx_routes_origins_dests ON routes(origin_id, dest_id);

-- Individual predictions
CREATE TABLE IF NOT EXISTS predictions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  airline_id INT REFERENCES airlines(id),
  route_id INT REFERENCES routes(id),
  flight_date DATE NOT NULL,
  scheduled_dep_time TIME NOT NULL,
  predicted_delayed BOOLEAN NOT NULL,
  delay_probability DECIMAL(5, 4),
  confidence VARCHAR(50),
  model_version VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_predictions_airline ON predictions(airline_id);
CREATE INDEX IF NOT EXISTS idx_predictions_route ON predictions(route_id);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(flight_date);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at DESC);

-- Batch upload tracking
CREATE TABLE IF NOT EXISTS batch_uploads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  file_name VARCHAR(255) NOT NULL,
  file_path VARCHAR(255),
  status VARCHAR(50) DEFAULT 'pending',
  total_rows INT,
  processed_rows INT DEFAULT 0,
  delayed_count INT DEFAULT 0,
  on_time_count INT DEFAULT 0,
  error_message TEXT,
  results_json JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_batch_uploads_status ON batch_uploads(status);
CREATE INDEX IF NOT EXISTS idx_batch_uploads_created ON batch_uploads(created_at DESC);

-- Explainability factors per prediction
CREATE TABLE IF NOT EXISTS explainability_factors (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  prediction_id UUID REFERENCES predictions(id) ON DELETE CASCADE,
  feature_name VARCHAR(100) NOT NULL,
  impact_magnitude DECIMAL(6, 4),
  direction VARCHAR(20),
  rank INT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_factors_prediction ON explainability_factors(prediction_id);

-- Model version metadata
CREATE TABLE IF NOT EXISTS model_metadata (
  id SERIAL PRIMARY KEY,
  model_version VARCHAR(20) UNIQUE NOT NULL,
  model_file_path VARCHAR(255),
  training_data_range VARCHAR(50),
  roc_auc DECIMAL(5, 4),
  accuracy DECIMAL(5, 4),
  precision DECIMAL(5, 4),
  recall DECIMAL(5, 4),
  total_features INT,
  feature_list JSONB,
  confusion_matrix JSONB,
  confusion_matrix_image_path VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  notes TEXT
);

-- Global feature importance per model version
CREATE TABLE IF NOT EXISTS feature_importance (
  id SERIAL PRIMARY KEY,
  model_version VARCHAR(20) REFERENCES model_metadata(model_version),
  feature_name VARCHAR(100) NOT NULL,
  importance_score DECIMAL(8, 6),
  rank INT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(model_version, feature_name)
);


-- ─── SEED DATA: Airlines ──────────────────────────────────

INSERT INTO airlines (code, name) VALUES
  ('Air Wisconsin Airlines Corp', 'Air Wisconsin Airlines Corp'),
  ('Alaska Airlines Inc.', 'Alaska Airlines Inc.'),
  ('Allegiant Air', 'Allegiant Air'),
  ('American Airlines Inc.', 'American Airlines Inc.'),
  ('Capital Cargo International', 'Capital Cargo International'),
  ('Comair Inc.', 'Comair Inc.'),
  ('Commutair Aka Champlain Enterprises, Inc.', 'Commutair Aka Champlain Enterprises, Inc.'),
  ('Delta Air Lines Inc.', 'Delta Air Lines Inc.'),
  ('Endeavor Air Inc.', 'Endeavor Air Inc.'),
  ('Envoy Air', 'Envoy Air'),
  ('Frontier Airlines Inc.', 'Frontier Airlines Inc.'),
  ('GoJet Airlines, LLC d/b/a United Express', 'GoJet Airlines, LLC d/b/a United Express'),
  ('Hawaiian Airlines Inc.', 'Hawaiian Airlines Inc.'),
  ('JetBlue Airways', 'JetBlue Airways'),
  ('Mesa Airlines Inc.', 'Mesa Airlines Inc.'),
  ('Republic Airlines', 'Republic Airlines'),
  ('SkyWest Airlines Inc.', 'SkyWest Airlines Inc.'),
  ('Southwest Airlines Co.', 'Southwest Airlines Co.'),
  ('Spirit Air Lines', 'Spirit Air Lines')
ON CONFLICT (code) DO NOTHING;


-- ─── SEED DATA: Airports (Major US airports) ─────────────

INSERT INTO airports (code, name, city, state, latitude, longitude) VALUES
  ('ATL', 'Hartsfield-Jackson Atlanta Intl', 'Atlanta', 'GA', 33.6407, -84.4277),
  ('AUS', 'Austin-Bergstrom Intl', 'Austin', 'TX', 30.1945, -97.6699),
  ('BNA', 'Nashville Intl', 'Nashville', 'TN', 36.1263, -86.6774),
  ('BOS', 'Boston Logan Intl', 'Boston', 'MA', 42.3656, -71.0096),
  ('BWI', 'Baltimore-Washington Intl', 'Baltimore', 'MD', 39.1754, -76.6684),
  ('CLE', 'Cleveland Hopkins Intl', 'Cleveland', 'OH', 41.4058, -81.8539),
  ('CLT', 'Charlotte Douglas Intl', 'Charlotte', 'NC', 35.2140, -80.9431),
  ('CVG', 'Cincinnati/N KY Intl', 'Cincinnati', 'OH', 39.0488, -84.6678),
  ('DCA', 'Ronald Reagan Washington Ntl', 'Arlington', 'VA', 38.8512, -77.0402),
  ('DEN', 'Denver Intl', 'Denver', 'CO', 39.8561, -104.6737),
  ('DFW', 'Dallas/Fort Worth Intl', 'Dallas', 'TX', 32.8998, -97.0403),
  ('DTW', 'Detroit Metro Wayne County', 'Detroit', 'MI', 42.2124, -83.3534),
  ('EWR', 'Newark Liberty Intl', 'Newark', 'NJ', 40.6895, -74.1745),
  ('FLL', 'Fort Lauderdale-Hollywood Intl', 'Fort Lauderdale', 'FL', 26.0742, -80.1506),
  ('HNL', 'Daniel K Inouye Intl', 'Honolulu', 'HI', 21.3187, -157.9224),
  ('HOU', 'William P Hobby', 'Houston', 'TX', 29.6454, -95.2789),
  ('IAD', 'Washington Dulles Intl', 'Dulles', 'VA', 38.9531, -77.4565),
  ('IAH', 'George Bush Intercontinental', 'Houston', 'TX', 29.9902, -95.3368),
  ('JFK', 'John F Kennedy Intl', 'New York', 'NY', 40.6413, -73.7781),
  ('LAS', 'Harry Reid Intl', 'Las Vegas', 'NV', 36.0840, -115.1537),
  ('LAX', 'Los Angeles Intl', 'Los Angeles', 'CA', 33.9425, -118.4081),
  ('LGA', 'LaGuardia', 'New York', 'NY', 40.7769, -73.8740),
  ('MCI', 'Kansas City Intl', 'Kansas City', 'MO', 39.2976, -94.7139),
  ('MCO', 'Orlando Intl', 'Orlando', 'FL', 28.4312, -81.3081),
  ('MDW', 'Chicago Midway Intl', 'Chicago', 'IL', 41.7868, -87.7522),
  ('MEM', 'Memphis Intl', 'Memphis', 'TN', 35.0421, -89.9767),
  ('MIA', 'Miami Intl', 'Miami', 'FL', 25.7959, -80.2870),
  ('MKE', 'General Mitchell Intl', 'Milwaukee', 'WI', 42.9472, -87.8966),
  ('MSP', 'Minneapolis-Saint Paul Intl', 'Minneapolis', 'MN', 44.8848, -93.2223),
  ('MSY', 'Louis Armstrong New Orleans Intl', 'New Orleans', 'LA', 29.9934, -90.2580),
  ('OAK', 'Oakland Intl', 'Oakland', 'CA', 37.7213, -122.2208),
  ('ONT', 'Ontario Intl', 'Ontario', 'CA', 34.0560, -117.6012),
  ('ORD', 'Chicago O Hare Intl', 'Chicago', 'IL', 41.9742, -87.9073),
  ('PHL', 'Philadelphia Intl', 'Philadelphia', 'PA', 39.8744, -75.2424),
  ('PHX', 'Phoenix Sky Harbor Intl', 'Phoenix', 'AZ', 33.4373, -112.0078),
  ('PIT', 'Pittsburgh Intl', 'Pittsburgh', 'PA', 40.4915, -80.2329),
  ('RDU', 'Raleigh-Durham Intl', 'Raleigh', 'NC', 35.8776, -78.7875),
  ('SAN', 'San Diego Intl', 'San Diego', 'CA', 32.7338, -117.1933),
  ('SAT', 'San Antonio Intl', 'San Antonio', 'TX', 29.5337, -98.4698),
  ('SEA', 'Seattle-Tacoma Intl', 'Seattle', 'WA', 47.4502, -122.3088),
  ('SFO', 'San Francisco Intl', 'San Francisco', 'CA', 37.6213, -122.3790),
  ('SLC', 'Salt Lake City Intl', 'Salt Lake City', 'UT', 40.7899, -111.9791),
  ('SMF', 'Sacramento Intl', 'Sacramento', 'CA', 38.6954, -121.5908),
  ('SNA', 'John Wayne-Orange County Intl', 'Santa Ana', 'CA', 33.6757, -117.8678),
  ('STL', 'St Louis Lambert Intl', 'St. Louis', 'MO', 38.7487, -90.3700),
  ('TPA', 'Tampa Intl', 'Tampa', 'FL', 27.9755, -82.5332),
  ('TUS', 'Tucson Intl', 'Tucson', 'AZ', 32.1161, -110.9410)
ON CONFLICT (code) DO NOTHING;


-- ─── SEED: Model Metadata ─────────────────────────────────

INSERT INTO model_metadata (
  model_version, training_data_range, roc_auc, accuracy,
  precision, recall, total_features, feature_list,
  confusion_matrix, is_active, notes
) VALUES (
  '1.0',
  '2018-2022',
  0.6720,
  0.8241,
  0.5900,
  0.0100,
  9,
  '["Airline", "Origin", "Dest", "Distance", "Month", "DayofMonth", "DayOfWeek", "DepHour", "ArrHour"]'::jsonb,
  '{"tn": 932298, "fp": 1391, "fn": 198212, "tp": 2002}'::jsonb,
  true,
  'XGBoost binary classifier trained on US domestic flights 2018-2022 (200K sample). Predicts whether arrival delay >= 15 minutes. Accuracy: 82.41%, ROC-AUC: 0.672'
)
ON CONFLICT (model_version) DO NOTHING;


-- ─── ROW LEVEL SECURITY (Optional) ────────────────────────
-- Uncomment these policies when Supabase Auth is configured.

-- ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can see own predictions"
--   ON predictions FOR SELECT
--   USING (auth.uid() = user_id OR user_id IS NULL);

-- ALTER TABLE batch_uploads ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can see own batch uploads"
--   ON batch_uploads FOR SELECT
--   USING (auth.uid() = user_id OR user_id IS NULL);
