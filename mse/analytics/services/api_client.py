# analytics/services/api_client.py
import time
from typing import Any, Dict, Optional

import requests
from django.conf import settings

# WNBA base URL (per openapi.yml)
BASE_URL = "https://api.balldontlie.io/wnba/v1"


def _get_api_key() -> str:
    """
    Try settings.BALLDONTLIE_API_KEY first, otherwise fall back to the
    key you provided explicitly so the app works out of the box.
    """
    return (
        getattr(settings, "BALLDONTLIE_API_KEY", None)
        or "65efc18f-c315-4399-a6bc-e72ab4afc65b"
    )


def get(endpoint: str, params: Optional[Dict[str, Any]] = None, retries: int = 5) -> Dict[str, Any]:
    """
    Simple GET wrapper with retry support for the BallDontLie WNBA API.
    Uses:
        - BASE_URL = https://api.balldontlie.io/wnba/v1
        - Authorization: <API_KEY>   (no 'Bearer')
    """
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    headers = {"Authorization": _get_api_key()}
    params = params or {}

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers, timeout=30)

        print("🔍 FETCH:", response.url)
        print("🔍 STATUS:", response.status_code)

        # Rate limiting
        if response.status_code == 429:
            wait = 2 ** attempt
            print(f"⏳ Rate limit hit. Waiting {wait} seconds...")
            time.sleep(wait)
            continue

        try:
            response.raise_for_status()
        except Exception as e:
            print("❌ REQUEST FAILED:", e)
            raise

        return response.json()

    raise Exception("❌ Max retries exceeded (API rate limit still blocking)")


def paginate_players(per_page: int = 100, max_pages: int = 50):
    """
    Stable paginator for WNBA /players endpoint.
    We avoid cursor-based pagination (too aggressive rate limiting)
    and use simple page=1,2,3,... pagination.

    Stops when:
      - no data returned
      - we hit max_pages
      - API rate limit persists
    """
    page = 1
    while page <= max_pages:
        params = {"per_page": per_page, "page": page}
        try:
            data = get("players", params=params, retries=5)
        except Exception as exc:
            print(f"❌ players page={page} failed: {exc}")
            break

        items = data.get("data", [])
        if not items:
            break  # no more data

        for item in items:
            yield item

        page += 1



def paginate(endpoint: str, base_params: Optional[Dict[str, Any]] = None, retries: int = 5):
    """
    Generic paginator that tries to support both 'page'-based and 'cursor'-based
    pagination styles used by BallDontLie.

    - If response.meta.next_cursor exists → use ?cursor=...
    - Else, fall back to page/current_page style.
    """
    params: Dict[str, Any] = dict(base_params or {})
    page = 1
    cursor: Optional[int] = None

    while True:
        if cursor is not None:
            # Cursor-based paging
            params["cursor"] = cursor
            params.pop("page", None)
        else:
            # Page-based paging
            params["page"] = page

        data = get(endpoint, params=params, retries=retries)
        items = data.get("data", []) or []
        if not items:
            break

        for item in items:
            yield item

        meta = data.get("meta") or {}

        # Cursor-based
        next_cursor = meta.get("next_cursor")
        if next_cursor:
            cursor = next_cursor
            continue

        # Page-based
        total_pages = meta.get("total_pages")
        current_page = meta.get("current_page")
        next_page = meta.get("next_page")

        # If explicit next_page
        if next_page and (total_pages is None or next_page <= total_pages):
            page = next_page
            cursor = None
            continue

        # Fallback: increment until we hit total_pages (if present)
        if total_pages and current_page and current_page < total_pages:
            page = current_page + 1
            cursor = None
            continue

        # No more data
        break
