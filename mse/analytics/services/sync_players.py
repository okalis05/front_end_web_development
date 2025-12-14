# analytics/services/sync_players.py
from typing import Dict, Optional

from django.db import transaction

from analytics.models import Player, Team
from .api_client import paginate_players


def _get_or_create_team(team_payload: Optional[dict]) -> Optional[Team]:
    if not team_payload:
        return None

    defaults: Dict[str, str] = {
        "name": team_payload.get("name") or "",
        "full_name": team_payload.get("full_name")
        or f"{team_payload.get('city', '')} {team_payload.get('name', '')}".strip(),
        "city": team_payload.get("city") or "",
        "abbreviation": team_payload.get("abbreviation") or "",
        "conference": team_payload.get("conference") or "",
        "division": team_payload.get("division") or "",
    }

    team, _ = Team.objects.update_or_create(
        external_id=str(team_payload["id"]),
        defaults=defaults,
    )
    return team

def sync_players() -> int:
    count = 0

    with transaction.atomic():
        for p in paginate_players(per_page=100, max_pages=50):
            team = _get_or_create_team(p.get("team"))

            Player.objects.update_or_create(
                external_id=str(p["id"]),
                defaults={
                    "team": team,
                    "first_name": p.get("first_name") or "",
                    "last_name": p.get("last_name") or "",
                    "jersey": p.get("jersey_number") or "",
                    "position": p.get("position_abbreviation")
                    or p.get("position")
                    or "",
                    "height": p.get("height") or "",
                    "weight": p.get("weight") or "",
                    "age": p.get("age"),
                    "headshot_url": "",
                },
            )
            count += 1

    print(f"✅ PLAYERS SYNCED: {count}")
    return count
