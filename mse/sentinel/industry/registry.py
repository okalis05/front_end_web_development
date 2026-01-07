import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent / "configs"
ALLOWED = ("sports", "mortgage", "retail", "healthcare")

def _load(key: str) -> dict:
    if key not in ALLOWED:
        raise KeyError(key)
    p = CONFIG_DIR / f"{key}.json"
    if not p.exists():
        raise KeyError(key)
    return json.loads(p.read_text(encoding="utf-8"))

def list_industries() -> list[dict]:
    out = []
    for k in ALLOWED:
        cfg = _load(k)
        out.append({"key": cfg["key"], "label": cfg["label"], "tagline": cfg["tagline"]})
    return out

def get_industry_config(key: str) -> dict:
    return _load(key)
