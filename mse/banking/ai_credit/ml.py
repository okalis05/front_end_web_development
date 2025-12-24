from __future__ import annotations
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

NUMERIC = [
    "loan_amnt",
    "int_rate",
    "annual_inc",
    "dti",
    "open_acc",
    "revol_bal",
    "total_acc",
    "delinq_2yrs",
    "pub_rec",
]

CATEGORICAL = [
    "term",
    "emp_length",
    "home_ownership",
    "purpose",
]

def build_pipeline() -> Pipeline:
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    pre = ColumnTransformer([
        ("num", num_pipe, NUMERIC),
        ("cat", cat_pipe, CATEGORICAL),
    ])

    model = LogisticRegression(max_iter=2500, n_jobs=None)
    return Pipeline([("prep", pre), ("model", model)])
