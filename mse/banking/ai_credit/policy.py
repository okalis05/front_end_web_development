from __future__ import annotations

def recommend_terms(prob_default: float, requested_amount: float) -> dict:
    amt = float(requested_amount or 0)

    if prob_default < 0.10:
        return {
            "risk_tier": "LOW",
            "decision": "APPROVE",
            "apr": 6.2,
            "term_months": 60,
            "max_amount": amt,
            "down_payment": int(0.05 * amt),
            "explainability": {
                "summary": "Low predicted default risk with strong affordability indicators.",
                "drivers": [
                    "Debt-to-income ratio within preferred band",
                    "Stable income signals",
                    "Limited recent derogatory history indicators",
                ],
                "policy_notes": [
                    "Eligible for standard pricing and standard term",
                    "Longer term permitted for low-risk tier",
                ],
            },
        }

    if prob_default < 0.25:
        return {
            "risk_tier": "MEDIUM",
            "decision": "REVIEW",
            "apr": 9.5,
            "term_months": 48,
            "max_amount": amt * 0.85,
            "down_payment": int(0.10 * amt),
            "explainability": {
                "summary": "Moderate risk indicators require tighter structure and verification.",
                "drivers": [
                    "Elevated debt-to-income ratio",
                    "Mixed credit-history indicators",
                ],
                "policy_notes": [
                    "Shorter term required under medium-risk policy",
                    "Higher down payment mitigates loss severity",
                ],
            },
        }

    return {
        "risk_tier": "HIGH",
        "decision": "DECLINE",
        "apr": None,
        "term_months": None,
        "max_amount": 0,
        "down_payment": None,
        "explainability": {
            "summary": "High predicted default risk exceeds acceptable lending thresholds.",
            "drivers": [
                "High DTI / weak affordability indicators",
                "Derogatory history indicators above tolerance",
            ],
            "policy_notes": [
                "Application exceeds high-risk cutoff",
                "Manual exception review possible for secured offers only",
            ],
        },
    }
