# analytics/services/wnba_client.py
import os
import time
import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)


class WNBAClient:
    """
    Thin wrapper around the BallDontLie WNBA API.

    Docs: https://api.balldontlie.io/wnba/v1/...
    - Teams:   /teams
    - Players: /players
    - Games:   /games
    """

    BASE_URL = "https://api.balldontlie.io/wnba/v1"

    def __init__(self) -> None:
        api_key = getattr(settings, "BALLDONTLIE_API_KEY", None) or os.getenv(
            "BALLDONTLIE_API_KEY"
        )
        if not api_key:
            raise RuntimeError(
                "BALLDONTLIE_API_KEY is not set. "
                "Add it to your .env and load it in settings.py."
            )

        # IMPORTANT: docs say header is literally Authorization: YOUR_API_KEY
        self.headers = {"Authorization": api_key}

    def _get(self, endpoint: str, params: dict | None = None, max_retries: int = 3):
        """
        Low-level GET with:
        - correct base URL
        - auth header
        - rate-limit backoff
        - cursor-aware meta handling
        """
        if params is None:
            params = {}

        url = f"{self.BASE_URL}/{endpoint}"

        for attempt in range(1, max_retries + 1):
            resp = requests.get(url, headers=self.headers, params=params, timeout=15)

            # Helpful debugging
            if resp.status_code == 401:
                logger.error(
                    "WNBA API 401 Unauthorized for %s. "
                    "Check BALLDONTLIE_API_KEY and that your account has WNBA access.",
                    url,
                )
                resp.raise_for_status()

            if resp.status_code == 404:
                logger.error("WNBA API 404 Not Found for %s", url)
                resp.raise_for_status()

            if resp.status_code == 429:
                wait = 2**attempt
                logger.warning(
                    "WNBA API 429 Too Many Requests for %s. Sleeping %s seconds...",
                    url,
                    wait,
                )
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()
            return data.get("data", []), data.get("meta", {}) or {}

        raise RuntimeError(f"Max retries exceeded for {url}")

    # ---------- Public helpers ----------

    def get_teams(self) -> list[dict]:
        # Teams are small; no pagination needed.
        data, _ = self._get("teams", params={"per_page": 100})
        return data

    def iter_players(
        self,
        per_page: int = 100,
        team_ids: list[int] | None = None,
        limit: int | None = None,
    ):
        """
        Cursor-based iteration over /players
        """
        cursor = None
        fetched = 0

        while True:
            params: dict[str, object] = {"per_page": per_page}
            if cursor is not None:
                params["cursor"] = cursor

            if team_ids:
                # ?team_ids[]=1&team_ids[]=2...
                for i, tid in enumerate(team_ids):
                    params[f"team_ids[{i}]"] = tid

            data, meta = self._get("players", params=params)
            if not data:
                break

            for row in data:
                yield row
                fetched += 1
                if limit is not None and fetched >= limit:
                    return

            cursor = meta.get("next_cursor")
            if not cursor:
                break

    def iter_games(
        self,
        season: int | None = None,
        team_ids: list[int] | None = None,
        per_page: int = 100,
    ):
        """
        Cursor-based iteration over /games
        """
        cursor = None

        while True:
            params: dict[str, object] = {"per_page": per_page}
            if season is not None:
                # docs: ?seasons[]=2024&seasons[]=2025
                params["seasons[]"] = season

            if cursor is not None:
                params["cursor"] = cursor

            if team_ids:
                for i, tid in enumerate(team_ids):
                    params[f"team_ids[{i}]"] = tid

            data, meta = self._get("games", params=params)
            if not data:
                break

            for row in data:
                yield row

            cursor = meta.get("next_cursor")
            if not cursor:
                break
