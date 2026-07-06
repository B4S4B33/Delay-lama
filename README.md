# ✈️ US Flight Delay Predictor

ML-powered flight delay prediction for US domestic flights with explainability, airline comparison, and batch processing.

## 🏗️ Architecture

```
Client (React)  →  FastAPI Backend  →  Supabase (PostgreSQL)
                       ↓
              XGBoost ML Model
```

**Tech Stack:**
- **Frontend:** React 18 + CSS Variables (Light/Dark mode)
- **Backend:** FastAPI (Python 3.10+) + Uvicorn
- **Database:** Supabase (PostgreSQL 14+)
- **ML:** XGBoost binary classifier (trained on 2018-2022 flight data)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account (free tier works)

### 1. Clone & Setup

```bash
# Clone the repository
git clone <repo-url>
cd flight-delay-predictor
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy model file
cp ../output/flight_delay_xgb.json .

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials (see SUPABASE_SETUP_GUIDE.md)

# Start the server
python main.py
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API URL and Supabase keys

# Start development server
npm start
```

Frontend runs at: http://localhost:3000

### 4. Database Setup

Follow the [Supabase Setup Guide](SUPABASE_SETUP_GUIDE.md) to:
1. Create a Supabase project
2. Run the SQL schema
3. Seed the database

## 📊 Features

### Single Flight Prediction
- Select airline, origin, destination, date, and time
- Get instant delay probability with confidence level
- View top 3 factors influencing the prediction

### Airline Comparison
- Compare predicted delay risk across airlines for the same route
- Side-by-side visualization of delay probabilities

### Batch Prediction
- Upload a CSV file with multiple flights
- Process hundreds of flights at once
- Download results with delay/on-time counts

### Explainability
- Every prediction shows the top 3 contributing factors
- Factors are ranked by impact with direction (increases/decreases risk)

### Dark Mode
- Full dark mode support across all components
- Toggle in the header, persisted in session storage
- WCAG AA contrast ratios in both themes

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment & Supabase config
│   ├── models.py            # Pydantic request/response schemas
│   ├── database.py          # Database wrapper
│   ├── ml_engine.py         # XGBoost model loading & prediction
│   ├── explainability.py    # Feature importance extraction
│   ├── supabase_queries.py  # DB query helpers
│   ├── batch_processor.py   # CSV batch processing
│   ├── seed_db.py           # Database seeding script
│   ├── schema.sql           # SQL DDL + seed data
│   ├── routes/
│   │   ├── predict.py       # /predict, /compare-airlines
│   │   ├── batch.py         # /predict-batch, /batch-status
│   │   ├── metadata.py      # /metadata, /feature-importance
│   │   └── health.py        # /health
│   ├── utils/
│   │   ├── validators.py    # Input validation
│   │   ├── error_handlers.py # Custom exceptions
│   │   └── feature_engineering.py # Feature preprocessing
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app with theme context
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── PredictionForm.jsx
│   │   │   ├── PredictionResult.jsx
│   │   │   ├── ExplainabilityPanel.jsx
│   │   │   ├── HistoricalRouteStats.jsx
│   │   │   ├── AirlineComparison.jsx
│   │   │   ├── BatchUpload.jsx
│   │   │   ├── ModelInfo.jsx
│   │   │   ├── ScopeDisclaimer.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── hooks/
│   │   │   ├── useTheme.js
│   │   │   ├── useLocalStorage.js
│   │   │   └── usePrediction.js
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   └── components.css
│   │   ├── utils/
│   │   │   ├── api.js
│   │   │   └── formatting.js
│   │   └── constants/
│   │       └── config.js
│   └── package.json
│
├── data/                    # Training data (CSV files)
├── output/                  # Trained model files
├── SUPABASE_SETUP_GUIDE.md  # Database setup instructions
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Single flight delay prediction |
| POST | `/compare-airlines` | Compare airlines on a route |
| POST | `/predict-batch` | Upload CSV for batch prediction |
| GET | `/batch-status/{id}` | Check batch upload status |
| GET | `/metadata` | Model performance metrics |
| GET | `/feature-importance` | Global feature importance |
| GET | `/airlines` | List all airlines |
| GET | `/airports` | List all airports |
| GET | `/health` | Health check |

Full interactive docs at: http://localhost:8000/docs

## 🧠 Model Details

- **Algorithm:** XGBoost (binary classifier)
- **Target:** `ArrDel15` — Will the flight arrive 15+ minutes late?
- **Training Data:** US domestic flights 2018-2022 (~200K sample)
- **Features:** Month, Day, DayOfWeek, Airline, Origin, Dest, Distance, DepHour, ArrHour
- **Categorical Support:** XGBoost native categorical encoding

## ⚠️ Limitations

- **US Domestic Only:** Trained exclusively on US domestic flights
- **No Weather Data:** Does not account for real-time weather conditions
- **No ATC Data:** Air traffic control delays not included
- **Historical Bias:** Predictions reflect patterns from 2018-2022 data
- **Not for Navigation:** This is an educational/portfolio project, not a flight planning tool

## 📄 License

MIT License — see LICENSE file for details.
