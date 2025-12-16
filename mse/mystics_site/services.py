from __future__ import annotations

import os
import requests
from typing import Any, Dict, Optional

BASE = "https://api.balldontlie.io/wnba/v1"

class APIError(RuntimeError):
    pass

def _headers() -> Dict[str, str]:
    key = os.getenv("BALDONTLIE_API_KEY", "").strip()
    if not key:
        raise APIError("Missing BALDONTLIE_API_KEY env var.")
    return {
        "Authorization": key,
        "Accept": "application/json",
    }


def get_json(path: str, params: Optional[dict] = None) -> Dict[str, Any]:
    url = f"{BASE}{path}"
    r = requests.get(url, headers=_headers(), params=params or {}, timeout=30)
    if r.status_code >= 400:
        raise APIError(f"API {r.status_code}: {r.text[:300]}")
    return r.json()

def paged(path: str, params: Optional[dict] = None, per_page: int = 100):
    cursor = 0
    while True:
        p = dict(params or {})
        p["per_page"] = per_page
        if cursor:
            p["cursor"] = cursor
        data = get_json(path, p)
        for row in data.get("data", []):
            yield row
        meta = data.get("meta") or {}
        cursor = meta.get("next_cursor")
        if not cursor:
            break
