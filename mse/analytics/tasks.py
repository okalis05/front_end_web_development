# analytics/tasks.py
import logging
from typing import Optional

from celery import shared_task
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from analytics.models import Game, Team, TeamSeasonStat
from analytics.services.sync_games import sync_games
from analytics.services.sync_players import sync_players
from analytics.services.sync_teams import sync_teams

logger = logging.getLogger(__name__)


@shared_task
def refresh_mystics_data(season: Optional[int] = None) -> None:
    """
    Periodic Celery task that:

    1. Syncs all WNBA teams, players, and games from BallDontLie WNBA API.
    2. Recomputes basic team season stats (PPG only) from the Game table.

    This keeps your existing dashboards working using only endpoints allowed
    by your API key (teams, players, games).
    """
    if season is None:
        season = timezone.now().year

    logger.info("Refreshing WNBA data for season %s via BallDontLie", season)

    teams_count = sync_teams()
    players_count = sync_players()
    games_count = sync_games(season=season)

    logger.info(
        "Sync complete – Teams: %s, Players: %s, Games: %s",
        teams_count,
        players_count,
        games_count,
    )

    # Recompute TeamSeasonStat (PPG) from Game model
    with transaction.atomic():
        TeamSeasonStat.objects.filter(season=season).delete()

        for team in Team.objects.all():
            games_qs = Game.objects.filter(season=season).filter(
                Q(home_team=team) | Q(visitor_team=team)
            )

            games = list(games_qs)
            if not games:
                continue

            total_points = 0
            for g in games:
                if g.home_team_id == team.id:
                    total_points += g.home_team_score or 0
                elif g.visitor_team_id == team.id:
                    total_points += g.visitor_team_score or 0

            games_played = len(games)
            ppg = total_points / games_played if games_played else 0.0

            TeamSeasonStat.objects.update_or_create(
                team=team,
                season=season,
                defaults={
                    "ppg": ppg,
                    # These require advanced stats; we leave them null.
                    "rpg": None,
                    "apg": None,
                    "net_rating": None,
                    "off_rating": None,
                    "def_rating": None,
                },
            )

    logger.info("TeamSeasonStat recompute finished for season %s", season)
