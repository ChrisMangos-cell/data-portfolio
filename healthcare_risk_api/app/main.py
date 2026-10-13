from pathlib import Path
from typing import List, Literal
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ValidationInfo, field_validator
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "artifacts" / "cardio_risk_pipeline.joblib"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model artifact not found at {MODEL_PATH}")

pipeline = joblib.load(MODEL_PATH)

app = FastAPI(
    title="Cardiovascular Clinical Risk Prediction API",
    description="Production ML inference service for cardiovascular risk triage using calibrated decision thresholds.",
    version="1.0.0"
)

class PatientFeatures(BaseModel):
    age_years: float = Field(..., ge=18.0, le=110.0, description="Age in years")
    gender: Literal["Male", "Female"] = Field(..., description="Biological sex")
    height_cm: float = Field(..., ge=100.0, le=250.0, description="Height in centimeters")
    weight_kg: float = Field(..., ge=30.0, le=300.0, description="Weight in kilograms")
    systolic_bp: int = Field(..., ge=70, le=240, description="Systolic blood pressure (mmHg)")
    diastolic_bp: int = Field(..., ge=40, le=160, description="Diastolic blood pressure (mmHg)")
    cholesterol_level: Literal["Normal", "Above Normal", "Well Above Normal"] = Field(
        ..., description="Serum cholesterol clinical categorization"
    )
    glucose_level: Literal["Normal", "Above Normal", "Well Above Normal"] = Field(
        ..., description="Fasting glucose clinical categorization"
    )
    is_smoker: int = Field(..., ge=0, le=1, description="Smoking status flag (0 or 1)")
    is_alcohol_consumer: int = Field(..., ge=0, le=1, description="Alcohol intake flag (0 or 1)")
    is_physically_active: int = Field(..., ge=0, le=1, description="Regular exercise flag (0 or 1)")

    @field_validator("diastolic_bp")
    @classmethod
    def validate_bp_coherence(cls, diastolic: int, info: ValidationInfo):
        systolic = info.data.get("systolic_bp") if info.data else None
        if systolic is not None and diastolic >= systolic:
            raise ValueError("diastolic_bp must be strictly less than systolic_bp")
        return diastolic

class PredictionResponse(BaseModel):
    risk_probability: float
    decision_threshold: float
    clinical_risk_tier: str
    flagged_for_intervention: bool
    computed_bmi: float

class BatchPredictionResponse(BaseModel):
    total_processed: int
    high_risk_count: int
    predictions: List[PredictionResponse]

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "healthy",
        "service": "cardio_risk_api",
        "model_loaded": pipeline is not None
    }

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
def predict_patient_risk(patient: PatientFeatures, threshold: float = 0.40):
    try:
        computed_bmi = round(patient.weight_kg / ((patient.height_cm / 100.0) ** 2), 2)
        
        input_data = pd.DataFrame([{
            "age_years": patient.age_years,
            "gender": patient.gender,
            "height_cm": patient.height_cm,
            "weight_kg": patient.weight_kg,
            "bmi": computed_bmi,
            "systolic_bp": patient.systolic_bp,
            "diastolic_bp": patient.diastolic_bp,
            "cholesterol_level": patient.cholesterol_level,
            "glucose_level": patient.glucose_level,
            "is_smoker": patient.is_smoker,
            "is_alcohol_consumer": patient.is_alcohol_consumer,
            "is_physically_active": patient.is_physically_active
        }])
        
        prob = float(pipeline.predict_proba(input_data)[0, 1])
        is_high_risk = prob >= threshold
        
        if prob >= 0.70:
            tier = "High Risk (Immediate Review)"
        elif prob >= 0.40:
            tier = "Moderate Risk (Screening Indicated)"
        else:
            tier = "Low Risk (Standard Care)"
            
        return PredictionResponse(
            risk_probability=round(prob, 4),
            decision_threshold=threshold,
            clinical_risk_tier=tier,
            flagged_for_intervention=is_high_risk,
            computed_bmi=computed_bmi
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(exc)}")

@app.post("/predict/batch", response_model=BatchPredictionResponse, status_code=status.HTTP_200_OK)
def predict_batch_risk(patients: List[PatientFeatures], threshold: float = 0.40):
    results = [predict_patient_risk(p, threshold) for p in patients]
    high_risk_count = sum(1 for r in results if r.flagged_for_intervention)
    return BatchPredictionResponse(
        total_processed=len(results),
        high_risk_count=high_risk_count,
        predictions=results
    )
