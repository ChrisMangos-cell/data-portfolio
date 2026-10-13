from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "clean_patients.parquet"
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "cardio_risk_pipeline.joblib"

def train_and_export():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Parquet dataset not found at {DATA_PATH}")

    print(f"Loading clinical cohort from {DATA_PATH}...")
    df = pd.read_parquet(DATA_PATH)
    print(f"Loaded {len(df):,} patient records.")

    # Target and Features
    target_col = "has_cardio_disease"
    drop_cols = [col for col in ["patient_id", target_col] if col in df.columns]
    X = df.drop(columns=drop_cols)
    y = df[target_col]

    num_cols = ["age_years", "height_cm", "weight_kg", "bmi", "systolic_bp", "diastolic_bp"]
    cat_cols = ["gender", "cholesterol_level", "glucose_level"]
    bin_cols = ["is_smoker", "is_alcohol_consumer", "is_physically_active"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), cat_cols),
            ("bin", "passthrough", bin_cols)
        ]
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", HistGradientBoostingClassifier(
            random_state=42, max_iter=250, learning_rate=0.08, min_samples_leaf=30
        ))
    ])

    print("Fitting champion HistGradientBoosting pipeline locally...")
    pipeline.fit(X_train, y_train)

    y_probs = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_probs)
    ap = average_precision_score(y_test, y_probs)
    print(f"Local Validation: ROC-AUC = {auc:.4f} | PR-AUC = {ap:.4f}")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Champion pipeline successfully serialized -> {MODEL_PATH}")

if __name__ == "__main__":
    train_and_export()
