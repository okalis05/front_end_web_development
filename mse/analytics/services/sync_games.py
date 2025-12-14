# analytics/services/sync_games.py
from datetime import datetime
from typing import Dict

from django.db import transaction
from django.utils.dateparse import parse_datetime

from analytics.models import Game, Team
from .api_client import paginate


def _get_or_create_team(team_data: Dict) -> Team:
    defaults = {
        "name": team_data.get("name") or "",
        "full_name": team_data.get("full_name")
        or f"{team_data.get('city', '')} {team_data.get('name', '')}".strip(),
        "city": team_data.get("city") or "",
        "abbreviation": team_data.get("abbreviation") or "",
        "conference": team_data.get("conference") or "",
        "division": team_data.get("division") or "",
    }

    team, _ = Team.objects.update_or_create(
        external_id=str(team_data["id"]),
        defaults=defaults,
    )
    return team


def _parse_date(dt_str: str) -> datetime:
    # BallDontLie returns ISO strings; parse_datetime handles Z/offsets.
    dt = parse_datetime(dt_str)
    if dt is None:
        dt = datetime.utcnow()
    return dt


def sync_games(season: int = 2024) -> int:
    """
    Sync games for a given season from BallDontLie WNBA API.

    Uses pagination via api_client.paginate and stores into Game model.
    Only fields that exist on your Game model are used.
    """
    count = 0

    params = {
        "per_page": 100,
        "seasons[]": season,  # BallDontLie uses `seasons[]` for filtering by year
    }

    with transaction.atomic():
        for g in paginate("games", base_params=params):
            home_team_data = g["home_team"]
            visitor_team_data = g["visitor_team"]

            home_team = _get_or_create_team(home_team_data)
            visitor_team = _get_or_create_team(visitor_team_data)

            date_obj = _parse_date(g["date"])

            # Align to your Game model fields:
            # external_id, date, home_team, visitor_team,
            # home_team_score, visitor_team_score, season, status
            Game.objects.update_or_create(
                external_id=int(g["id"]),
                defaults={
                    "date": date_obj,
                    "season": g.get("season"),
                    "status": g.get("status", ""),
                    "home_team": home_team,
                    "visitor_team": visitor_team,
                    "home_team_score": g.get("home_team_score", 0),
                    "visitor_team_score": g.get("visitor_team_score", 0),
                },
            )
            count += 1

    print(f"✅ GAMES SYNCED: {count}")
    return count
