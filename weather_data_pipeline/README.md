# 🌦️ Automated Weather Data Ingestion & Analytics Pipeline

A production-grade, resilient time-series ETL pipeline extracting multi-variable meteorological metrics from the Open-Meteo REST API, normalizing nested JSON payloads, and executing idempotent staging loads into an embedded DuckDB analytical database.

---

## 🏛️ Pipeline Architecture

```
       [ Open-Meteo REST API ]
                  │
        (HTTPS / JSON Payload)
                  │
                  ▼
       [ extract_api.py ]  <─── Exponential Backoff (urllib3 / Retry Adapter)
                  │
          (Parallel Arrays)
                  │
                  ▼
     [ transform_load.py ] <─── Schema Normalization & UTC ISO Casting
                  │
       (Idempotent INSERT OR REPLACE)
                  │
                  ▼
     ┌────────────────────────────┐
     │ DuckDB Analytical Engine   │
     ├────────────────────────────┤
     │ • dim_locations            │
     │ • stg_weather_observations │
     │ • v_daily_weather_summary  │
     │ • v_rolling_weather_metrics│
     └────────────────────────────┘
                  ▲
                  │
         [ test_pipeline.py ]  <─── Automated Assertions (PK Uniqueness, Domain Bounds)
```

---

## 🔑 Core Data Engineering Principles

### 1. Resilient API Consumption
- **Exponential Backoff:** Configured HTTP sessions with adaptive retry strategies targeting transient gateway failures (500, 502, 503, 504) and rate limits (429).
- **Standardized Temporal Horizon:** Extracted multi-day observation windows across international cities, converting local timestamps into unified UTC time-series.

### 2. Idempotent Ingestion Pattern
- Staging tables implement a composite primary key contract: `(location_id, observation_timestamp)`.
- Re-executing pipeline jobs uses atomic `INSERT OR REPLACE` transactions, preventing duplicate records upon repeated execution.

### 3. Automated Data Quality Assertions
The test suite (`test_pipeline.py`) validates critical pipeline invariants:
- **Primary Key Uniqueness:** Verifies zero duplicate time-series keys.
- **Null Constraint Assertions:** Enforces zero null values in critical fields (`location_id`, `observation_timestamp`, `temperature_2m`).
- **Physical Domain Boundaries:** Asserts observations obey physical limits (e.g., 0% <= Humidity <= 100%, Wind Speed >= 0).
- **Temporal Continuity:** Confirms continuous, unbroken hourly record sequences across monitored cities.

---

## 📁 Repository Directory Structure

```
weather_data_pipeline/
├── sql/
│   ├── 00_staging_ddl.sql         # Relational staging schema & composite keys
│   └── 01_weather_metrics.sql     # Analytical rollups & moving window views
├── scripts/
│   ├── extract_api.py             # Resilient REST client with retry logic
│   ├── transform_load.py          # Array unnesting, typing & idempotent upsert
│   └── run_pipeline.py            # Master CLI pipeline orchestrator
├── tests/
│   └── test_pipeline.py           # Automated schema & data quality test assertions
├── logs/
│   └── pipeline.log               # Pipeline execution logs
└── README.md                      # Architecture & engineering documentation
```

---

## 🚀 Execution & Quickstart

```bash
# 1. Install dependencies
pip install duckdb requests pandas pyarrow pytest

# 2. Execute end-to-end pipeline
python weather_data_pipeline/scripts/run_pipeline.py

# 3. Run automated data quality test suite
pytest weather_data_pipeline/tests/test_pipeline.py
```