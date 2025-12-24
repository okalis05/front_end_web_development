from __future__ import annotations
from typing import List, Dict, Any, Optional
import requests

# Public catalog APIs:
# - NHTSA vPIC: makes/models (very stable)
# - CarQuery: trims and years (no key, JSONP style sometimes)

NHTSA_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles"
CARQUERY = "https://www.carqueryapi.com/api/0.3/"

def nhtsa_makes() -> List[str]:
    url = f"{NHTSA_BASE}/getallmakes?format=json"
    data = requests.get(url, timeout=20).json()
    return sorted({m["Make_Name"] for m in data.get("Results", []) if m.get("Make_Name")})

def nhtsa_models(make: str, year: int | None = None) -> List[str]:
    if year:
        url = f"{NHTSA_BASE}/GetModelsForMakeYear/make/{make}/modelyear/{year}?format=json"
    else:
        url = f"{NHTSA_BASE}/GetModelsForMake/{make}?format=json"
    data = requests.get(url, timeout=20).json()
    return sorted({m["Model_Name"] for m in data.get("Results", []) if m.get("Model_Name")})

def carquery_trims(make: str, model: str, year: int | None = None) -> List[Dict[str, Any]]:
    params = {"cmd":"getTrims", "make":make, "model":model}
    if year:
        params["year"] = str(year)

    r = requests.get(CARQUERY, params=params, timeout=20)
    text = r.text.strip()

    # CarQuery sometimes returns JSONP: "?(...json...)"
    if text.startswith("?(") and text.endswith(");"):
        text = text[2:-2]

    data = None
    try:
        data = r.json()
    except Exception:
        import json
        data = json.loads(text)

    trims = data.get("Trims", []) or []
    out = []
    for t in trims[:40]:
        out.append({
            "make": t.get("make_display") or make,
            "model": t.get("model_name") or model,
            "year": int(t.get("model_year") or year or 0) or None,
            "trim": t.get("model_trim") or "",
            "body": t.get("model_body") or "",
            "engine": t.get("model_engine_cc") or "",
            "fuel": t.get("model_engine_fuel") or "",
        })
    return out

def estimate_price_band(year: int | None, tier: str = "Core") -> Dict[str, int]:
    # simple deterministic band (replace later with paid pricing API)
    base = 26000 if tier == "Core" else 34000
    if year and year < 2016:
        base -= 8000
    elif year and year < 2020:
        base -= 4000
    return {"low": max(6000, base - 4500), "high": base + 6500}
