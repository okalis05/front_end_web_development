from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional, Iterator

import requests

BASE = "https://api.balldontlie.io/wnba/v1"


class APIError(RuntimeError):
    pass


def _api_key() -> str:
    return (
        (os.getenv("BALLDONTLIE_API_KEY") or "").strip()
        or (os.getenv("BALDONTLIE_API_KEY") or "").strip()  # tolerate typo
    )


def _headers() -> Dict[str, str]:
    key = _api_key()
    if not key:
        raise APIError("Missing BALLDONTLIE_API_KEY env var.")
    return {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }


def get_json(
    path: str,
    params: Optional[dict] = None,
    timeout: int = 30,
    max_retries: int = 6,
) -> Dict[str, Any]:
    url = f"{BASE}{path}"
    params = params or {}

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, headers=_headers(), params=params, timeout=timeout)

            # Rate-limit handling
            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                sleep_for = int(retry_after) if retry_after else min(2**attempt, 30)
                time.sleep(sleep_for)
                continue

            if r.status_code >= 400:
                raise APIError(f"API {r.status_code}: {r.text[:300]}")

            return r.json()

        except requests.RequestException:
            sleep_for = min(2**attempt, 30)
            time.sleep(sleep_for)

    raise APIError(f"API request failed after {max_retries} retries: {url}")


def paged(path: str, params: Optional[dict] = None, per_page: int = 25) -> Iterator[dict]:
    cursor = None

    while True:
        p = dict(params or {})
        p["per_page"] = per_page
        if cursor:
            p["cursor"] = cursor

        data = get_json(path, p)
        rows = data.get("data", [])
        if not rows:
            break

        for row in rows:
            yield row

        meta = data.get("meta") or {}
        cursor = meta.get("next_cursor")
        if not cursor:
            break

        # throttle to avoid 429
        time.sleep(1.25)
