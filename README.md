# 🚀 Data Analytics Portfolio

Personal portfolio showcasing end-to-end data analytics, engineering, and predictive modeling projects.

---

## 📊 Project 1: E-Commerce Revenue & Retention Engine
📁 **Repository Directory:** [`sales_customer_analytics/`](./sales_customer_analytics)  
🛠️ **Tech Stack:** DuckDB SQL, Python (Pandas, Plotly), Streamlit  
📈 **Dataset:** 100k+ Transactions (Olist Brazilian E-Commerce)

### Executive Results Summary

| Analysis Area | Metric / Threshold | Core Commercial Finding |
| :--- | :--- | :--- |
| **Cohort Retention** | **< 0.7% Month 1 Decay** | Repeat purchase rates dropped below 0.7% across all 18 monthly acquisition cohorts, proving the platform functions as a one-time transaction engine rather than a habitual repeat marketplace. |
| **RFM Segmentation** | **~R$ 4.4M GMV Concentration** | The *Dormant Big Spenders* and *At-Risk High-Value* segments accounted for ~R$ 4.4M in revenue despite having less than half the volume of general buyers, highlighting the primary audience for automated win-back marketing. |
| **Pareto Distribution** | **Top 23% Categories = 80% GMV** | 80% of marketplace gross value is concentrated in only 23% of product categories (led by Health & Beauty, Watches, and Bed/Bath), exposing heavy supplier-side vulnerability. |
| **Interactive BI App** | **Multi-Tab Dashboard** | Built a Streamlit analytics dashboard backed by pre-aggregated Parquet data and DuckDB for fast query execution and KPI filtering. |

---

## 🌦️ Project 2: Weather Data Ingestion & Analytics Pipeline
📁 **Repository Directory:** [`weather_data_pipeline/`](./weather_data_pipeline)  
🛠️ **Tech Stack:** Python (Requests, urllib3 Retry Adapters), DuckDB SQL, Pytest, REST APIs  
📈 **Data Scope:** 1,800 Hourly Observations Across 5 Global Metros (Open-Meteo API)

### Executive Engineering Summary

| Engineering Layer | Implementation / Metric | Core Technical Outcome |
| :--- | :--- | :--- |
| **Resilient API Extraction** | **urllib3 Retry + Exponential Backoff** | Configured a fault-tolerant REST client handling rate limits (`429`) and gateway timeouts (`5xx`), extracting 15-day continuous hourly payloads across Melbourne, Sydney, London, New York, and Tokyo. |
| **Idempotent Staging Layer** | **DuckDB Composite Key Upserts** | Built relational schema enforced by composite primary keys `(location_id, observation_timestamp)`, preventing duplicate records during pipeline re-runs via atomic `INSERT OR REPLACE`. |
| **Analytical Window Views** | **Daily Rollups & Moving Averages** | Engineered SQL analytical views computing diurnal temperature swings, cumulative precipitation, and 3-day / 7-day rolling moving averages to smooth short-term variance. |
| **Automated Data Quality** | **Pytest Assertion Suite** | Implemented assertions validating primary key uniqueness, zero critical nulls, physical boundary conditions (-60°C to 60°C, 0–100% humidity), and hourly temporal continuity. |

---

## 🗺️ Upcoming Portfolio Roadmap

* **Project 1 (Month 1): E-Commerce Revenue & Retention Engine** — DuckDB SQL, RFM, Cohort Retention, Streamlit Dashboard. ✅ *(Completed)*
* **Project 2 (Month 2): Weather Data Pipeline & Ingestion Engine** — Core ETL, staging schema, and automated tests complete. 🟡 *(Weeks 7–8 Automation & Anomaly Detection In Progress)*
* **Project 3 (Month 3): Spotify Music Clustering** — Unsupervised audio feature clustering with Scikit-Learn and SQL. ⚪ *(Planned)*
* **Project 4 (Month 3): Healthcare Risk Prediction & API** — Classification model deployed via FastAPI. ⚪ *(Planned)*
