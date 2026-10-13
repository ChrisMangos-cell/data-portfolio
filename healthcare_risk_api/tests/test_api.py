import pytest
from fastapi.testclient import TestClient
from healthcare_risk_api.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["model_loaded"] is True

def test_low_risk_patient_prediction():
    payload = {
        "age_years": 28.0,
        "gender": "Female",
        "height_cm": 168.0,
        "weight_kg": 62.0,
        "systolic_bp": 115,
        "diastolic_bp": 75,
        "cholesterol_level": "Normal",
        "glucose_level": "Normal",
        "is_smoker": 0,
        "is_alcohol_consumer": 0,
        "is_physically_active": 1
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_probability"] < 0.40
    assert data["flagged_for_intervention"] is False
    assert data["clinical_risk_tier"] == "Low Risk (Standard Care)"
    assert data["computed_bmi"] == 21.97

def test_high_risk_patient_prediction():
    payload = {
        "age_years": 62.0,
        "gender": "Male",
        "height_cm": 174.0,
        "weight_kg": 96.0,
        "systolic_bp": 165,
        "diastolic_bp": 105,
        "cholesterol_level": "Well Above Normal",
        "glucose_level": "Above Normal",
        "is_smoker": 1,
        "is_alcohol_consumer": 1,
        "is_physically_active": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_probability"] >= 0.40
    assert data["flagged_for_intervention"] is True
    assert "Risk" in data["clinical_risk_tier"]

def test_blood_pressure_coherence_validation():
    # Diastolic greater than Systolic must trigger HTTP 422 Unprocessable Entity
    invalid_payload = {
        "age_years": 45.0,
        "gender": "Male",
        "height_cm": 175.0,
        "weight_kg": 75.0,
        "systolic_bp": 80,
        "diastolic_bp": 120,
        "cholesterol_level": "Normal",
        "glucose_level": "Normal",
        "is_smoker": 0,
        "is_alcohol_consumer": 0,
        "is_physically_active": 1
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422
