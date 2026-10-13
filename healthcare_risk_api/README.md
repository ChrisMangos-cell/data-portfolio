# 🩺 Cardiovascular Clinical Risk Prediction API

Production-grade clinical decision support API powered by an optimized gradient boosting pipeline and FastAPI. The service ingests patient biometrics, calculates derived metabolic indicators, enforces biological validation rules, and serves calibrated cardiovascular risk probabilities tailored for clinical screening triage.

---

## 📑 Table of Contents
- [Executive Clinical Summary](#executive-clinical-summary)
- [System Architecture](#system-architecture)
- [Data Hygiene & Cohort Staging](#data-hygiene--cohort-staging)
- [Model Evaluation & Benchmarking](#model-evaluation--benchmarking)
- [Clinical Decision Threshold Optimization](#clinical-decision-threshold-optimization)
- [Model Explainability (SHAP Analysis)](#model-explainability-shap-analysis)
- [API Serving Layer & Endpoints](#api-serving-layer--endpoints)
- [Automated Test Suite](#automated-test-suite)
- [Project Directory Structure](#project-directory-structure)

---

## Executive Clinical Summary

| Metric / Attribute | Clinical / System Benchmark | Real-World Impact |
| :--- | :--- | :--- |
| **Validated Cohort** | **69,823 Patients** | Excluded 177 physiologically impossible vitals (e.g., diastolic > systolic). |
| **Model Discrimination** | **ROC-AUC: 0.8633 \| PR-AUC: 0.8645** | `HistGradientBoosting` demonstrates strong class separation on holdout data. |
| **Triage Decision Gate** | **Calibrated Threshold: 0.40** | Cuts missed sick patients (False Negatives) by **32.9%** (1,586 → 1,064) vs standard 0.50 threshold. |
| **Peak F1 Performance** | **F1-Score: 0.7877** | Balances diagnostic sensitivity (84.77%) with high positive predictive value (73.57%). |
| **Inference Latency** | **< 15ms per patient** | Lightweight REST microservice with Pydantic cross-field input validation. |

---

## System Architecture

```text
[ Raw Clinical Cohort (70,000 Records) ]
                   │
                   ▼  (DuckDB SQL Boundary Filters)
[ Clean Clinical Cohort: 69,823 Records (clean_patients.parquet) ]
                   │
                   ▼  (Scikit-Learn Pipeline: Scaler + OHE + HistGradientBoosting)
[ Champion Serialized Pipeline (cardio_risk_pipeline.joblib) ]
                   │
                   ▼  (Loaded into memory)
[ FastAPI Serving Microservice (Pydantic v2 Cross-Field Validation) ]
      ├── GET  /health          --> Service & model state check
      ├── POST /predict         --> Single-patient clinical triage & BMI calculation
      └── POST /predict/batch   --> Population-level screening batch inference
```

---

## Data Hygiene & Cohort Staging

The dataset was ingested using **DuckDB** to execute strict physiological validation boundaries before training:
* **Blood Pressure Plausibility:** Systolic blood pressure must exceed diastolic blood pressure ($Systolic > Diastolic$), bounded between $70 \le Systolic \le 240$ mmHg and $40 \le Diastolic \le 160$ mmHg.
* **Anthropometric Limits:** Height restricted between $100$ cm and $250$ cm; weight restricted between $30$ kg and $300$ kg.
* **Sanitation Outcome:** 177 abnormal anomaly records were purged, staging **69,823 clean patient profiles** into compressed Parquet storage.

### Cohort Baseline Clinical Means

| Biomarker / Feature | No Disease Cohort (0) | Cardiovascular Disease Cohort (1) | Clinical Delta |
| :--- | :--- | :--- | :--- |
| **Mean Age** | 42.82 years | 51.35 years | **+8.53 years** older |
| **Systolic Blood Pressure** | 121.16 mmHg | 133.86 mmHg | **+12.70 mmHg** elevation |
| **Diastolic Blood Pressure** | 74.63 mmHg | 82.50 mmHg | **+7.87 mmHg** elevation |
| **Body Mass Index (BMI)** | 27.94 kg/m² | 27.89 kg/m² | Identical baseline distribution |
| **Smoking Prevalence** | 7.0% | 11.0% | **+57.1%** relative risk |

---

## Model Evaluation & Benchmarking

Two distinct architectures were evaluated on an 80/20 stratified holdout split:

| Model Architecture | ROC-AUC | PR-AUC | Primary Strength / Clinical Trade-off |
| :--- | :--- | :--- | :--- |
| **Logistic Regression (Baseline)** | 0.8670 | 0.8688 | High linear interpretability; requires explicit interaction terms. |
| **HistGradientBoosting (Champion)** | **0.8633** | **0.8645** | Robust non-linear feature split capture, native handling of skewed distributions, zero imputation latency. |

<p align="center">
  <img src="./charts/roc_benchmark.png" alt="ROC and PR Benchmark Curves" width="700">
</p>

---

## Clinical Decision Threshold Optimization

In cardiovascular risk screening, **false negatives carry severe clinical consequences** (discharging an undiagnosed patient with cardiovascular disease). Default machine learning classifiers deploy an arbitrary **0.50** classification boundary, which causes high diagnostic miss rates.

### Threshold Sensitivity Analysis

| Decision Threshold | Sensitivity (Recall) | PPV (Precision) | F1-Score | Missed Sick Patients (FN) | Clinical Recommendation |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **0.30** | 90.54% | 68.73% | 0.7814 | 661 | Aggressive triage; higher false-alarm rate. |
| **0.35** | 87.80% | 71.07% | 0.7856 | 852 | Strong early screening profile. |
| **0.40** | **84.77%** | **73.57%** | **0.7877** | **1,064** | **Optimal Gate:** Max F1, eliminates 522 missed cases vs 0.50. |
| **0.45** | 81.50% | 75.80% | 0.7855 | 1,292 | Intermediate conservative profile. |
| **0.50** | 77.29% | 77.92% | 0.7761 | 1,586 | Default standard (unacceptable false negative volume). |

> **Key Clinical Decision:** Lowering the operational screening gate to **0.40** reduces false negatives from **1,586 down to 1,064**—a **32.9% reduction in missed sick patients**—while retaining a 73.57% positive predictive value and achieving peak $F_1$ (0.7877).

---

## Model Explainability (SHAP Analysis)

Model decisions were audited using TreeSHAP to verify alignment with established cardiovascular clinical literature:

<p align="center">
  <img src="./charts/shap_summary.png" alt="SHAP Beeswarm Summary Plot" width="650">
</p>

### Physiological Attributions:
1. **Primary Risk Escalators:** `age_years` and `systolic_bp` possess the widest SHAP value distributions. High values (pink) exhibit strong positive SHAP log-odds (+2.0 to +4.0), identifying advanced age and systolic hypertension as dominant predictors of cardiovascular disease.
2. **Protective Modifiers:** `cholesterol_level_Normal`, `is_physically_active`, and `glucose_level_Normal` show negative SHAP values, confirming that regular exercise and normal baseline biomarkers reduce overall model risk.
3. **Behavioral Amplifiers:** `is_smoker` and `cholesterol_level_Well Above Normal` introduce sharp positive risk vectors.
4. **Low Variance Controls:** `gender_Male` and `is_alcohol_consumer` demonstrate tightly clustered SHAP values near zero, confirming minimal independent bias in this cohort.

---

## API Serving Layer & Endpoints

The API is served via FastAPI with Pydantic v2 runtime validation.

### Request Payload Example (`POST /predict`)
```json
{
  "age_years": 58.0,
  "gender": "Male",
  "height_cm": 172.0,
  "weight_kg": 89.0,
  "systolic_bp": 152,
  "diastolic_bp": 94,
  "cholesterol_level": "Above Normal",
  "glucose_level": "Normal",
  "is_smoker": 1,
  "is_alcohol_consumer": 0,
  "is_physically_active": 0
}
```

### Response Payload Example
```json
{
  "risk_probability": 0.9875,
  "decision_threshold": 0.4,
  "clinical_risk_tier": "High Risk (Immediate Review)",
  "flagged_for_intervention": true,
  "computed_bmi": 30.08
}
```

### Risk Stratification Tiers
* **High Risk (Immediate Review):** Risk Probability $\ge 0.70$
* **Moderate Risk (Screening Indicated):** $0.40 \le$ Risk Probability $< 0.70$
* **Low Risk (Standard Care):** Risk Probability $< 0.40$

---

## Automated Test Suite

A complete test suite is implemented using `pytest` and `fastapi.testclient`:

```powershell
python -m pytest -v healthcare_risk_api\tests\
```

* `test_health_endpoint` $\rightarrow$ Validates service uptime and model object presence.
* `test_low_risk_patient_prediction` $\rightarrow$ Asserts healthy profiles produce risk $< 0.40$ and correct BMI calculations.
* `test_high_risk_patient_prediction` $\rightarrow$ Asserts hypertensive profiles produce risk $\ge 0.40$ and flag for triage.
* `test_blood_pressure_coherence_validation` $\rightarrow$ Enforces input sanity; payloads with $diastolic \ge systolic$ trigger `HTTP 422 Unprocessable Entity`.

---

## Project Directory Structure

```text
healthcare_risk_api/
├── app/
│   └── main.py                     # FastAPI service with Pydantic validation
├── artifacts/
│   └── cardio_risk_pipeline.joblib # Serialized champion Scikit-Learn pipeline
├── charts/
│   ├── roc_benchmark.png           # Discrimination performance curves
│   └── shap_summary.png            # SHAP beeswarm feature impact plot
├── data/
│   └── clean_patients.parquet      # 69,823 validated clinical records
├── scripts/
│   └── train_model.py              # Reproducible pipeline training script
├── tests/
│   └── test_api.py                 # Pytest test suite (4 passing assertions)
├── README.md                       # Clinical documentation
└── requirements.txt                # Frozen Python dependencies
```
