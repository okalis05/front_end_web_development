# analytics/services/season_averages.py
import logging

logger = logging.getLogger(__name__)


def sync_season_averages(season: int = 2024) -> int:
    """
    Stub implementation. Your current API key only supports teams, players,
    and games – not season averages.

    We keep this function so any existing imports won't crash, but it just
    logs and returns 0.
    """
    logger.info(
        "Skipping sync_season_averages for season %s – "
        "current API key does not include season averages.", season
    )
    return 0
