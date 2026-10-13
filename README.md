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

## 🎧 Project 3: Spotify Music Clustering & Recommendation Engine
📁 **Repository Directory:** [`spotify_music_clustering/`](./spotify_music_clustering)  
🛠️ **Tech Stack:** Python (Scikit-Learn, Pandas, NumPy), DuckDB SQL, Matplotlib, Seaborn  
📈 **Dataset:** 32,800+ Spotify Tracks across 9 Continuous Audio Features

### Executive Results & Machine Learning Summary

| ML Layer | Technique / Metric | Core Outcome & Analytical Finding |
| :--- | :--- | :--- |
| **Feature Normalization** | **StandardScaler (μ=0, σ=1)** | Standardized unbounded metrics (`tempo` 35–240 BPM, `loudness` -46 to 1 dB) alongside bounded metrics (`energy`, `valence`), eliminating Euclidean distance distortion. |
| **Dimensionality Reduction** | **Principal Component Analysis** | Reduced 9 acoustic dimensions down to 6 orthogonal components while retaining **84.08%** of total catalog variance; projected 2D latent space capturing 40.68% variance. |
| **Cluster Optimization** | **Elbow SSE & Silhouette Score** | Evaluated $k \in [2, 10]$, identifying **$k = 6$** as the optimal inflection point ($S = 0.1573$) separating distinct musical archetypes without over-segmentation. |
| **Archetype Profiling** | **Centroid Z-Score Contrasts** | Segmented catalog into 6 discrete archetypes: Upbeat Pop (10.7k), Driving Rock/EDM (8.6k), Acoustic Downtempo (4.6k), Urban Hip-Hop (4.3k), Instrumental (2.5k), and Live Recordings (2.2k). |
| **Vector Search Engine** | **Cosine Similarity Retrieval** | Built content-based nearest neighbor recommendation engine retrieving acoustically identical songs ($S_{\cos} \ge 0.95$) with sub-second latency. |

---

## 🩺 Project 4: Healthcare Clinical Risk Prediction API
📁 **Repository Directory:** [`healthcare_risk_api/`](./healthcare_risk_api)  
🛠️ **Tech Stack:** Python (FastAPI, Scikit-Learn, Pydantic, DuckDB, Joblib, Pytest), Uvicorn, SHAP  
📈 **Dataset:** 69,823 Biologically Validated Clinical Records (Cardiovascular Disease Cohort)

### Executive Results & Machine Learning Serving Summary

| ML / Systems Layer | Technique / Metric | Core Clinical & Engineering Outcome |
| :--- | :--- | :--- |
| **Biological Boundary Cleaning** | **DuckDB SQL Staging** | Filtered 177 physiological outliers (records with systolic BP < diastolic BP or out-of-range vitals) from 70,000 raw entries, staging 69,823 clean patient profiles into Parquet. |
| **Predictive Modeling** | **HistGradientBoostingClassifier** | Trained an optimized gradient boosting pipeline achieving **0.8633 ROC-AUC** and **0.8645 PR-AUC** on stratified test holdouts, outperforming baseline Logistic Regression. |
| **Clinical Threshold Tuning** | **Optimized 0.40 Decision Gate** | Lowered standard 0.50 threshold to 0.40 to minimize clinical false negatives, reducing missed critical cases from 1,586 to 1,064 (a 32.9% reduction in missed sick patients) with an F1-score of 0.7877. |
| **Feature Attribution (XAI)** | **SHAP TreeExplainer** | Isolated systolic blood pressure and age as the dominant drivers increasing cardiovascular risk (+2 to +4 SHAP log-odds), with physical activity and baseline cholesterol acting as significant protective factors. |
| **Microservice Serving** | **FastAPI + Uvicorn** | Built production REST endpoints (`/predict`, `/predict/batch`) with Pydantic v2 validation enforcing dynamic BMI computation and cross-field blood pressure sanity checks. |
| **Automated Test Guardrails** | **Pytest TestClient Suite** | Implemented automated testing verifying `/health` availability, low/high-risk decision tier assertions, and HTTP 422 Unprocessable Entity error handling for biologically incoherent vitals. |

---

## 🗺️ Portfolio Roadmap

- **Project 1 (Month 1): E-Commerce Revenue & Retention Engine** — DuckDB SQL, RFM, Cohort Retention, Streamlit Dashboard. ✅ *(Completed)*
- **Project 2 (Month 2): Weather Data Pipeline & Ingestion Engine** — End-to-end API ETL, DuckDB staging, Prefect orchestration, CI/CD automation, and statistical anomaly detection. ✅ *(Completed)*
- **Project 3 (Month 3): Spotify Music Clustering** — Unsupervised audio feature clustering, PCA reduction, and cosine recommendation engine. ✅ *(Completed)*
- **Project 4 (Month 4): Healthcare Clinical Risk Prediction API** — Gradient boosting pipeline, DuckDB boundary cleaning, SHAP explainability, calibrated triage thresholds, and FastAPI serving layer with automated test suite. ✅ *(Completed)*
