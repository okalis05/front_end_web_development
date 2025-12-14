# analytics/services/sync_teams.py
from typing import Dict

from django.db import transaction

from analytics.models import Team
from .api_client import get


def sync_teams() -> int:
    """
    Sync all WNBA teams from BallDontLie WNBA API into Team model.
    Endpoint: GET /teams
    """
    response = get("teams", params={"per_page": 100})
    teams = response.get("data", []) or []
    count = 0

    with transaction.atomic():
        for t in teams:
            # API fields are similar to NBA: id, city, abbreviation, conference, division, full_name, name
            defaults: Dict[str, str] = {
                "name": t.get("name") or "",
                "full_name": t.get("full_name")
                or f"{t.get('city', '')} {t.get('name', '')}".strip(),
                "city": t.get("city") or "",
                "abbreviation": t.get("abbreviation") or "",
                "conference": t.get("conference") or "",
                "division": t.get("division") or "",
            }

            Team.objects.update_or_create(
                external_id=str(t["id"]),
                defaults=defaults,
            )
            count += 1

    print(f"✅ TEAMS SYNCED: {count}")
    return count

