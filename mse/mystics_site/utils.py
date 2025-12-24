from __future__ import annotations

from django.db.models import Q
from mystics_site.models import Team


def get_mystics() -> Team | None:
    """
    Safe lookup (never crashes pages).
    Uses exact match if available, else partial fallback.
    """
    # Try exact full_name (your preferred canonical value)
    team = Team.objects.filter(full_name="Washington Mystics").first()
    if team:
        return team

    # Fallback if API data uses slightly different naming
    return Team.objects.filter(
        Q(full_name__icontains="Mystics") | Q(name__icontains="Mystics")
    ).order_by("full_name").first()
