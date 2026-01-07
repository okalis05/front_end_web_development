from __future__ import annotations

import os
from typing import Tuple, Dict, Any

import joblib
import pandas as pd
from django.conf import settings
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score

from .ml import build_pipeline
from .models import CreditModelArtifact

ARTIFACT_DIR = os.path.join(settings.BASE_DIR, "banking", "ai_credit", "artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# LendingClub target mapping
GOOD_STATUSES = {"Fully Paid", "Current"}
BAD_STATUSES = {
    "Charged Off", "Default", "Late (31-120 days)", "Late (16-30 days)"
}

FEATURE_WHITELIST = [
    "loan_amnt", "term", "int_rate", "annual_inc", "dti",
    "emp_length", "home_ownership", "purpose",
    "open_acc", "revol_bal", "total_acc", "delinq_2yrs", "pub_rec",
]


# -------------------------
# Training
# -------------------------

def _prepare_target(df: pd.DataFrame) -> pd.Series:
    s = df["loan_status"].astype(str)
    return s.apply(lambda x: 0 if x in GOOD_STATUSES else 1)


def train_credit_model(csv_path: str, version: str = "v1") -> CreditModelArtifact:
    df = pd.read_csv(csv_path, low_memory=False)

    missing = [c for c in (FEATURE_WHITELIST + ["loan_status"]) if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")

    y = _prepare_target(df)
    X = df[FEATURE_WHITELIST].copy()

    pipe = build_pipeline()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pipe.fit(X_train, y_train)
    p = pipe.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, p)),
        "avg_precision": float(average_precision_score(y_test, p)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }

    path = os.path.join(ARTIFACT_DIR, f"credit_model_{version}.joblib")
    joblib.dump(pipe, path)

    CreditModelArtifact.objects.filter(is_active=True).update(is_active=False)

    artifact = CreditModelArtifact.objects.create(
        version=version,
        artifact_path=path,
        metrics=metrics,
        feature_schema={"features": FEATURE_WHITELIST},
        is_active=True,
    )
    return artifact


# -------------------------
# Inference
# -------------------------

def load_active_model() -> Tuple[Any, CreditModelArtifact]:
    artifact = (
        CreditModelArtifact.objects
        .filter(is_active=True)
        .order_by("-created_at")
        .first()
    )
    if not artifact:
        raise RuntimeError("No active credit model. Train one first.")

    pipe = joblib.load(artifact.artifact_path)
    return pipe, artifact


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Banking-grade feature normalization.
    Converts UI / API inputs → ML-safe numeric features.
    """
    p = payload.copy()

    # ------------------
    # TERM: "60 months" → 60
    # ------------------
    term = p.get("term")
    if isinstance(term, str):
        try:
            p["term"] = int(term.split()[0])
        except Exception:
            p["term"] = 60
    else:
        p["term"] = int(term) if term else 60

    # ------------------
    # EMPLOYMENT LENGTH → numeric years
    # ------------------
    emp = str(p.get("emp_length", "")).lower().strip()
    EMP_MAP = {
        "< 1 year": 0,
        "<1 year": 0,
        "1 year": 1,
        "2 years": 2,
        "3 years": 3,
        "4 years": 4,
        "5 years": 5,
        "6 years": 6,
        "7 years": 7,
        "8 years": 8,
        "9 years": 9,
        "10+ years": 10,
        "10 years": 10,
    }
    p["emp_length"] = EMP_MAP.get(emp, 10)

    # ------------------
    # HOME OWNERSHIP → numeric
    # ------------------
    HOME_MAP = {
        "RENT": 0,
        "MORTGAGE": 1,
        "OWN": 2,
        "OTHER": 0,
        "NONE": 0,
    }
    ho = str(p.get("home_ownership", "RENT")).upper()
    p["home_ownership"] = HOME_MAP.get(ho, 0)

    # ------------------
    # PURPOSE → numeric
    # ------------------
    PURPOSE_MAP = {
        "car": 0,
        "credit_card": 1,
        "debt_consolidation": 2,
        "home_improvement": 3,
        "major_purchase": 4,
        "other": 5,
    }
    purpose = str(p.get("purpose", "car")).lower()
    p["purpose"] = PURPOSE_MAP.get(purpose, 0)

    # ------------------
    # NUMERIC COERCIONS
    # ------------------
    for k in [
        "loan_amnt", "int_rate", "annual_inc", "dti",
        "open_acc", "revol_bal", "total_acc",
        "delinq_2yrs", "pub_rec",
    ]:
        try:
            p[k] = float(p.get(k, 0) or 0)
        except Exception:
            p[k] = 0.0

    return p




def score(payload: Dict[str, Any]) -> Dict[str, Any]:
    pipe, artifact = load_active_model()

    payload = _normalize_payload(payload)

    row = {k: payload.get(k) for k in FEATURE_WHITELIST}
    X = pd.DataFrame([row])

    prob = float(pipe.predict_proba(X)[0][1])

    return {
        "prob_default": prob,
        "model_version": artifact.version,
        "artifact": artifact,
    }
