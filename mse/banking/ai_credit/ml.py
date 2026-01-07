# banking/ai_credit/ml.py

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

NUMERIC_FEATURES = [
    "loan_amnt",
    "annual_inc",
    "dti",
    "int_rate",
    "open_acc",
    "revol_bal",
    "total_acc",
    "delinq_2yrs",
    "pub_rec",
]

CATEGORICAL_FEATURES = [
    "term",           # e.g. "36 months", "60 months"
    "purpose",        # e.g. "car", "credit_card"
    "home_ownership", # RENT / OWN / MORTGAGE
    "emp_length",     # "10+ years"
]

def build_pipeline() -> Pipeline:
    """
    Builds a production-safe credit scoring pipeline.
    Handles numeric + categorical features correctly.
    """

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    n_jobs=None,
                ),
            ),
        ]
    )

    return pipeline
