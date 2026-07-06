# ✈️ US Flight Delay Predictor
## Project Portfolio & System Analysis Report

---

### Executive Summary

The **US Flight Delay Predictor** is an end-to-end, machine learning-powered web application designed to predict flight delays of 15 minutes or more (`ArrDel15`) on US domestic routes. By integrating a high-performance **XGBoost Classifier** with a **FastAPI** backend, a **Supabase (PostgreSQL)** database, and a highly responsive **React** frontend, the system provides real-time single-flight predictions, multi-airline comparisons, batch processing (CSV/Excel), and feature-level explainability. 

This report outlines the architecture, data pipeline, machine learning model training, database schema design, and implementation walkthrough of the project submission.

---

### 1. System Architecture & Data Flow

The application follows a modern three-tier web architecture optimized for cloud deployment and minimal prediction latency.

```text
      +-------------------------------------------+
      |               User Browser                |
      +---------------------+---------------------+
                            | (HTTP Requests)
                            v
      +-------------------------------------------+
      |           React Frontend Client           |
      +---------------------+---------------------+
                            | (JSON APIs)
                            v
      +-------------------------------------------+
      |              FastAPI Backend              |
      |  +-------------------------------------+  |
      |  |  XGBoost Machine Learning Engine    |  |
      |  +-------------------------------------+  |
      |  |  Prediction Explainability Engine   |  |
      |  +-------------------------------------+  |
      |  |  CSV/Excel Batch Processor          |  |
      |  +-------------------------------------+  |
      +---------------------+---------------------+
                            | (SQL queries)
                            v
      +-------------------------------------------+
      |        Supabase PostgreSQL Database       |
      +-------------------------------------------+
```

#### Prediction Sequence Flow

The diagram below details the sequence of steps executed during a single flight prediction request:

```text
Passenger          React Client         FastAPI Backend       Supabase DB
    |                   |                      |                   |
 1. Input Flight Details|                      |                   |
    +------------------>|                      |                   |
    |                   | 2. POST /predict     |                   |
    |                   +--------------------->|                   |
    |                   |                      | 3. Query Route    |
    |                   |                      +------------------>|
    |                   |                      |                   |
    |                   |                      | 4. Return Stats   |
    |                   |                      |<------------------+
    |                   |                      |                   |
    |                   |                      | [Feature Eng.]    |
    |                   |                      | [Run XGBoost]     |
    |                   |                      | [Explain Pred.]   |
    |                   |                      |                   |
    |                   |                      | 5. Save logs      |
    |                   |                      +------------------>|
    |                   | 6. JSON Response     |                   |
    |                   |<---------------------+                   |
 7. Render Probability  |                      |                   |
    |<------------------+                      |                   |
```

---

### 2. Machine Learning Model Engineering

The predictive core of the system is a binary classification model built with **XGBoost (eXtreme Gradient Boosting)**.

#### A. Dataset Characteristics
The model is trained on historical US domestic flights spanning 2018 to 2022 (~10 GB of raw CSV data). The target variable is `ArrDel15` (1 if the flight arrived 15+ minutes late, 0 otherwise). Cancelled and diverted flights are excluded from training since arrival delays cannot be computed for them.

#### B. Memory-Optimized Training Pipeline
Training on a multi-gigabyte dataset in resource-constrained environments (like Google Colab's standard ~12.7 GB RAM instance) requires careful memory management:
* **Chunk-Based Loading:** Data is streamed in chunks of 150,000 rows at a time to prevent high peak memory usage.
* **Low-Precision Types:** Variables are mapped to compact memory footprints (e.g., `int8` for calendar dates, `int16` for time representations, and `float32` for distances).
* **Downsampling:** The training notebook includes a user-configurable sampling parameter (`SAMPLE_FRACTION = 0.2`) to dynamically extract representative training samples.
* **Garbage Collection:** Intermediate variables are deleted and python's `gc.collect()` is triggered manually.

#### C. Feature Engineering
The model utilizes a streamlined, leak-free feature set that can be known at the time of booking:

| Feature | Data Type | Description / Engineering |
| :--- | :--- | :--- |
| `Airline` | `category` | Operating carrier (categorical) |
| `Origin` | `category` | Origin Airport 3-letter IATA code (categorical) |
| `Dest` | `category` | Destination Airport 3-letter IATA code (categorical) |
| `Distance` | `float32` | Non-stop flight distance in miles (numerical) |
| `Month` | `int8` | Month of flight (1-12) to capture seasonal variation |
| `DayofMonth` | `int8` | Day of the month (1-31) |
| `DayOfWeek` | `int8` | Day of the week (1-7) to capture weekday/weekend congestion |
| `DepHour` | `int8` | Scheduled departure hour (0-23) extracted from military time |
| `ArrHour` | `int8` | Scheduled arrival hour (0-23) extracted from military time |

> [!NOTE]
> The training notebook supports toggling a `PREDICT_PRE_DEPARTURE` flag. If set to `False`, the model incorporates `DepDelayMinutes` (departure delay in minutes) as a post-departure feature. This provides a significant boost in performance (ROC-AUC > 0.90) but is only usable when predicting during/after flight departure.

#### D. Training & XGBoost Features
* **Native Categorical Support:** Features like `Airline`, `Origin`, and `Dest` are loaded as pandas `category` datatypes. XGBoost's `enable_categorical=True` parameter is utilized to partition categorical thresholds natively, avoiding memory-expensive one-hot encoding or arbitrary integer label assignment.
* **GPU Acceleration:** Configures the histogram tree-building method (`tree_method='hist'` or `'gpu_hist'`) using GPU hardware acceleration (`device='cuda'`) inside Colab.
* **Regularization & Early Stopping:** A stratified 10% validation split is used for validation during training. Training stops if evaluation log-loss fails to improve for 15 consecutive epochs, preventing overfitting.
* **Export Formats:** The final model is saved in both Python's native binary format (`.joblib`) and XGBoost's standardized `.json` format, ensuring portability.

---

### 3. Backend Architecture (FastAPI)

The backend provides high-throughput, low-latency endpoints using **FastAPI** and **Uvicorn**.

#### A. Prediction API (`/predict`)
This endpoint accepts airline, route, date, and scheduled time. The input is validated using **Pydantic** models, engineered into model features, and passed to the XGBoost engine.
* **Confidence Rating:** Classified as `high` if probability is extreme ($\ge 0.8$ or $\le 0.2$), `moderate` if it is close to the decision boundary ($0.4 \le p \le 0.6$), and `high` otherwise.
* **Route Benchmarking:** Simultaneously pulls historical delay statistics from PostgreSQL to give users context on typical route performance.

#### B. Explainability Engine (`explainability.py`)
To prevent the black-box effect common in machine learning models, the backend features a heuristic explainability engine. It extracts the top 3 global feature importances from the model (e.g., departure hour, airline, distance) and maps the individual flight values to directional impacts:
* **Departure Hour:** Scheduled peak hours (6 AM - 10 AM, 4 PM - 8 PM) are flagged as **increasing** delay risk due to airport congestion.
* **Arrival Hour:** Late night arrivals (5 PM - 11 PM) are flagged as **increasing** risk.
* **Distance:** Long-haul flights (>1,500 miles) are flagged as **decreasing** risk due to flight-duration buffers.
* **Month / Day of Week:** Friday/Sunday travel and holiday/summer months (June-August, Nov-Dec) are categorized as **increasing** delay risk.

#### C. Batch Processing (`batch_processor.py`)
Handles streaming CSV or Excel uploads. It parses inputs line-by-line, runs them through the XGBoost classifier, logs summary statistics (total, delayed, on-time, errors), and provides a structured JSON return payload.

---

### 4. Database Schema Design (Supabase/PostgreSQL)

The database, hosted on **Supabase**, acts as a reference directory and logs prediction transactions.

```text
 +------------------------+         +------------------------+
 |       AIRPORTS         |         |       AIRLINES         |
 +------------------------+         +------------------------+
 | id (PK) [Serial]       |         | id (PK) [Serial]       |
 | code (UK) [Varchar]    |         | code (UK) [Varchar]    |
 | name [Varchar]         |         | name [Varchar]         |
 | city [Varchar]         |         +-----------+------------+
 | state [Varchar]        |                     |
 +-----------+------------+                     |
             |                                  |
             | (1:N Origin/Dest)                |
             v                                  |
 +---------------------------+                  |
 |          ROUTES           |                  |
 +---------------------------+                  |
 | id (PK) [Serial]          |                  |
 | origin_id (FK) [Int]      |                  |
 | dest_id (FK) [Int]        |                  |
 | distance_miles [Int]      |                  |
 | historical_delay_rate     |                  |
 +-----------+---------------+                  |
             |                                  |
             | (1:N Route)                      | (1:N Airline)
             v                                  v
 +-----------------------------------------------------------+
 |                       PREDICTIONS                         |
 +-----------------------------------------------------------+
 | id (PK) [UUID]                                            |
 | airline_id (FK) [Int]                                     |
 | route_id (FK) [Int]                                       |
 | flight_date [Date]                                        |
 | scheduled_dep_time [Time]                                 |
 | predicted_delayed [Bool]                                  |
 | delay_probability [Decimal]                               |
 +---------------------------+-------------------------------+
                             |
                             | (1:N Prediction)
                             v
 +-----------------------------------------------------------+
 |                 EXPLAINABILITY_FACTORS                    |
 +-----------------------------------------------------------+
 | id (PK) [UUID]                                            |
 | prediction_id (FK) [UUID]                                 |
 | feature_name [Varchar]                                    |
 | impact_magnitude [Decimal]                                |
 | direction [Varchar]                                       |
 +-----------------------------------------------------------+
```

* **Index Optimization:** Database queries are speed-optimized through indexes:
  * Composite index `idx_routes_origins_dests` on `routes(origin_id, dest_id)` for lightning-fast historical route statistics lookups.
  * Indices on `predictions(airline_id)`, `predictions(route_id)`, and `predictions(created_at DESC)` to support fast dashboard queries.

---

### 5. Frontend Implementation (React)

The frontend is a single-page React 18 application centered on visual clarity, accessibility (WCAG AA contrast ratios), and responsive design.

* **Layout & Navigation:** Built with three responsive views:
  1. **Predict:** Features a modular form validation component alongside side-by-side explainability indicators and historical route charts.
  2. **Compare:** Compares multiple airlines on the selected route to help passengers pick the lowest-risk carrier.
  3. **Batch Upload:** An interactive file-drop area that gives immediate success/error progress feedback on flight batches.
* **Theme System:** Incorporates a lightweight custom vanilla CSS configuration with CSS custom variables, enabling clean transitions between **Light Mode** and **Dark Mode**.
* **Visuals:** Integrates responsive SVG charts, glassmorphism card panels, and smooth micro-animations on user inputs to deliver a premium interface.

---

### 6. System Limitations & Future Work

While highly functional, the US Flight Delay Predictor has specific constraints:
* **No Real-Time Weather Integration:** Weather conditions (snow, thunderstorms) account for over 50% of domestic flight delays but are not present in this model. Integrating a service like OpenWeatherMap to inject real-time forecasted weather during prediction is a high-priority future work item.
* **Lack of Air Traffic Control (ATC) Logs:** Airspace capacity delays are not represented in the historical data.
* **Historical Data Limits:** Predictions are based on flight schedules from 2018-2022, which may skew predictions for newly added flight paths.

---

### Summary Checklist of Submission Deliverables

- [x] **Jupyter Notebook (`flight_delay_xgboost.ipynb`)**: Completed memory-efficient training codebase with chunking, categorical configurations, and model saving cells.
- [x] **FastAPI Backend Structure (`backend/`)**: Model loading singleton, modular routes, and validation schemas.
- [x] **Supabase SQL Schema (`schema.sql`)**: Data definition scripts, reference inserts, and performance indexes.
- [x] **React Client (`frontend/`)**: Modern UI, light/dark modes, single-prediction dashboards, and batch-upload drag-and-drop.
- [x] **Project Analysis (`report.md`)**: Full technical review, flowchart diagrams, database model mapping, and verification checklist.
