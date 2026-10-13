# 🚀 Data Analytics & Engineering Portfolio

Personal portfolio showcasing end-to-end data analytics, engineering pipelines, and predictive modeling systems.

---

## 📊 Project 1: E-Commerce Revenue & Retention Engine
📁 **Repository Directory:** [`sales_customer_analytics/`](./sales_customer_analytics)  
🛠️ **Tech Stack:** DuckDB SQL, Python (Pandas, Plotly), Streamlit  
📈 **Dataset:** 100k+ Transactions (Olist Brazilian E-Commerce)

### Executive Results Summary

| Analysis Area | Metric / Threshold | Core Commercial Finding |
| :--- | :--- | :--- |
| **Cohort Retention** | **< 0.7% Month 1 Decay** | Repeat purchase rates dropped below 0.7% across all 18 monthly acquisition cohorts, proving the platform functions as an acquisition-dependent transaction engine rather than a habitual repeat marketplace. |
| **RFM Segmentation** | **~R$ 4.4M GMV Concentration** | The *Dormant Big Spenders* and *At-Risk High-Value* segments accounted for ~R$ 4.4M in revenue despite having less than half the volume of general buyers, highlighting the primary audience for automated win-back marketing. |
| **Pareto Distribution** | **Top 23% Categories = 80% GMV** | 80% of marketplace gross value is concentrated in only 23% of product categories (led by Health & Beauty, Watches, and Bed/Bath), exposing heavy supplier-side vulnerability. |
| **Interactive BI App** | **Multi-Tab Dashboard** | Built a Streamlit analytics dashboard backed by pre-aggregated Parquet data and DuckDB for sub-second KPI filtering. |

---

## 🌦️ Project 2: Weather Data Ingestion & Analytics Pipeline
📁 **Repository Directory:** [`weather_data_pipeline/`](./weather_data_pipeline)  
🛠️ **Tech Stack:** Python (Requests, Prefect, Pytest), DuckDB SQL, GitHub Actions, Matplotlib  
📈 **Data Scope:** 1,800+ Hourly Observations Across 5 Global Metros (Open-Meteo API)

### Executive Results & Engineering Summary

| Engineering Layer | Implementation / Metric | Core Outcome & Analytical Finding |
| :--- | :--- | :--- |
| **Resilient API Extraction** | **urllib3 Retry + Backoff** | Handled rate limits (`429`) and gateway timeouts (`5xx`) across continuous hourly payloads for Melbourne, Sydney, London, New York, and Tokyo. |
| **Stateful Watermarking** | **Incremental Timestamp Delta** | Automated boundary queries via `MAX(observation_timestamp)` in DuckDB, reducing redundant API egress and compute overhead. |
| **Idempotent Staging Layer** | **DuckDB Composite Key Upserts** | Enforced composite primary keys `(location_id, observation_timestamp)` to guarantee idempotent loads via atomic `INSERT OR REPLACE`. |
| **Workflow Orchestration** | **Prefect Flow DAG** | Managed state transitions and task retries across extraction, validation, and analytics DAG tasks in under 3 seconds per run. |
| **Automated CI/CD Cron** | **GitHub Actions Cloud Workflow** | Scheduled daily refresh jobs (06:00 UTC) executing headless incremental ingestion, view refreshes, and test guardrails. |
| **Statistical Anomaly Engine** | **Windowed Z-Scores (\|Z\| ≥ 2.5)** | Flagged 44 severe meteorological anomalies across 1,800 observations, including a +3.40σ Sydney heatwave (32.8°C), New York rain squalls (5.4 mm/hr), and London gale gusts (25.2 km/h). |
| **Automated Data Quality** | **Pytest Assertion Suite** | Enforced CI quality gates checking primary key uniqueness, zero critical nulls, physical domain bounds (-60°C to 60°C), and hourly continuity. |

---

## 🗺️ Portfolio Roadmap

* **Project 1 (Month 1): E-Commerce Revenue & Retention Engine** — DuckDB SQL, RFM, Cohort Retention, Streamlit Dashboard. ✅ *(Completed)*
* **Project 2 (Month 2): Weather Data Pipeline & Ingestion Engine** — End-to-end API ETL, DuckDB staging, Prefect orchestration, CI/CD automation, and statistical anomaly detection. ✅ *(Completed)*
* **Project 3 (Month 3): Spotify Music Clustering** — Unsupervised audio feature clustering with Scikit-Learn and SQL. ⚪ *(Planned)*
* **Project 4 (Month 3): Healthcare Risk Prediction & API** — Classification model deployed via FastAPI. ⚪ *(Planned)*
