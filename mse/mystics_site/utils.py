from __future__ import annotations

from django.db.models import Q
from mystics_site.models import Team


def get_mystics() -> Team | None:
    
    team = Team.objects.filter(full_name="Washington Mystics").first()
    if team:
        return team

    
    return Team.objects.filter(
        Q(full_name__icontains="Mystics") | Q(name__icontains="Mystics")
    ).order_by("full_name").first()
