from django.utils.dateparse import parse_datetime

from analytics.models import Game, Team
from .api_client import get


def sync_games(season: int = 2024):
    """
    Sync games for a given season from BallDontLie.
    Uses pagination: ?page= & per_page=
    """
    page = 1

    while True:
        response = get(
            "games", params={"page": page, "per_page": 100, "seasons[]": season}
        )
        data = response.get("data", [])

        if not data:
            break

        for g in data:
            home_team_data = g["home_team"]
            visitor_team_data = g["visitor_team"]

            home_team, _ = Team.objects.update_or_create(
                external_id=str(home_team_data["id"]),
                defaults={
                    "name": home_team_data["name"],
                    "full_name": home_team_data.get("full_name", "") or home_team_data["name"],
                    "city": home_team_data.get("city", ""),
                    "abbreviation": home_team_data.get("abbreviation", ""),
                    "conference": home_team_data.get("conference", "") or "",
                    "division": home_team_data.get("division", "") or "",
                },
            )

            visitor_team, _ = Team.objects.update_or_create(
                external_id=str(visitor_team_data["id"]),
                defaults={
                    "name": visitor_team_data["name"],
                    "full_name": visitor_team_data.get("full_name", "") or visitor_team_data["name"],
                    "city": visitor_team_data.get("city", ""),
                    "abbreviation": visitor_team_data.get("abbreviation", ""),
                    "conference": visitor_team_data.get("conference", "") or "",
                    "division": visitor_team_data.get("division", "") or "",
                },
            )

            date_obj = parse_datetime(g["date"])

            Game.objects.update_or_create(
                external_id=g["id"],
                defaults={
                    "date": date_obj,
                    "season": g["season"],
                    "period": g.get("period"),
                    "status": g.get("status", ""),
                    "home_team": home_team,
                    "visitor_team": visitor_team,
                    "home_score": g.get("home_team_score", 0),
                    "visitor_score": g.get("visitor_team_score", 0),
                },
            )

        page += 1

