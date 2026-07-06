# Supabase Setup Guide — US Flight Delay Predictor

This guide walks you through setting up Supabase for the Flight Delay Predictor application.

---

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in (or create an account)
2. Click **"New Project"**
3. Choose your organization (or create one)
4. Fill in project details:
   - **Project Name:** `flight-delay-predictor`
   - **Database Password:** Choose a strong password (save it!)
   - **Region:** Choose the closest region to your users
5. Click **"Create new project"**
6. Wait 1-2 minutes for the project to be provisioned

---

## 2. Get Your API Keys

Once your project is ready:

1. Go to **Settings** → **API** (in the left sidebar)
2. Copy the following values:

| Key | Location | Purpose |
|-----|----------|---------|
| **Project URL** | Settings → API → Project URL | `SUPABASE_URL` |
| **anon/public key** | Settings → API → Project API keys → `anon` `public` | `SUPABASE_KEY` |
| **service_role key** | Settings → API → Project API keys → `service_role` | `SUPABASE_SERVICE_KEY` |

> ⚠️ **Never expose the `service_role` key in client-side code.** It bypasses Row-Level Security.

---

## 3. Create Database Tables

### Option A: Using the SQL Editor (Recommended)

1. In your Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Copy the entire contents of `backend/schema.sql`
4. Paste it into the SQL editor
5. Click **"Run"** (or press Ctrl+Enter)

This will create all 8 tables, indexes, and seed data.

### Option B: Using the Table Editor

If you prefer a GUI approach, create each table manually through **Table Editor** → **New Table**:

**Tables to create (in order due to foreign keys):**
1. `airlines`
2. `airports`
3. `routes` (references airports)
4. `predictions` (references airlines, routes, auth.users)
5. `batch_uploads` (references auth.users)
6. `explainability_factors` (references predictions)
7. `model_metadata`
8. `feature_importance` (references model_metadata)

See `backend/schema.sql` for exact column definitions.

---

## 4. Verify Tables Were Created

1. Go to **Table Editor** in the Supabase dashboard
2. You should see all 8 tables listed
3. Click on `airlines` — you should see 16 airline records
4. Click on `airports` — you should see 46 airport records
5. Click on `model_metadata` — you should see 1 model version record

---

## 5. Configure Your Backend

Create a `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# FastAPI
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=True

# Model
MODEL_VERSION=1.0
MODEL_FILE_PATH=flight_delay_xgb.json
```

> **Important:** Copy the model file to the backend directory:
> ```bash
> cp output/flight_delay_xgb.json backend/
> ```

---

## 6. Seed Additional Data (Optional)

If you want to seed data programmatically instead of using the SQL editor:

```bash
cd backend
pip install -r requirements.txt
python seed_db.py
```

This will insert airlines, airports, model metadata, and feature importance records.

---

## 7. Configure Your Frontend

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key-here
```

---

## 8. Row-Level Security (Optional)

For production with user authentication, enable RLS policies:

```sql
-- Enable RLS on predictions table
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can see own predictions"
  ON predictions FOR SELECT
  USING (auth.uid() = user_id OR user_id IS NULL);

-- Enable RLS on batch_uploads table
ALTER TABLE batch_uploads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can see own batch uploads"
  ON batch_uploads FOR SELECT
  USING (auth.uid() = user_id OR user_id IS NULL);
```

> Note: RLS policies are commented out in `schema.sql` by default. Uncomment them when Supabase Auth is configured.

---

## 9. Test the Connection

Start the backend and check the health endpoint:

```bash
cd backend
python main.py
```

Then visit:
- **Health check:** http://localhost:8000/health
- **API docs:** http://localhost:8000/docs

The health endpoint should return:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "version": "1.0"
}
```

---

## 10. Troubleshooting

### "relation does not exist" error
- Tables haven't been created yet. Run the schema.sql in the SQL Editor.

### "permission denied for table" error
- You're using the `anon` key for server-side operations. Use the `service_role` key in `SUPABASE_SERVICE_KEY`.

### CORS errors
- Make sure `CORS_ORIGINS` in your backend `.env` matches your frontend URL.

### Model file not found
- Copy `output/flight_delay_xgb.json` to the `backend/` directory, or set `MODEL_FILE_PATH` to the correct path.

### Database connection check fails
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct.
- Check that your Supabase project is not paused (free tier pauses after inactivity).

---

## Database Schema Overview

```
airlines (16 rows)
  └── routes.origin_id → airports.id
  └── routes.dest_id → airports.id

airports (46 rows)

routes
  └── predictions.airline_id → airlines.id
  └── predictions.route_id → routes.id
  └── explainability_factors.prediction_id → predictions.id

batch_uploads

model_metadata
  └── feature_importance.model_version → model_metadata.model_version
```

---

## Quick Reference: Table Counts

| Table | Expected Rows | Description |
|-------|---------------|-------------|
| airlines | 16 | US carrier names |
| airports | 46 | Major US airports |
| routes | ~2,000+ | Airport pairs with stats |
| predictions | 0 (grows) | User predictions |
| batch_uploads | 0 (grows) | CSV upload history |
| explainability_factors | 0 (grows) | Per-prediction factors |
| model_metadata | 1 | Model v1.0 info |
| feature_importance | 9 | Global feature scores |
