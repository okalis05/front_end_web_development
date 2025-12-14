# analytics/services/sync_player_logs.py
import logging

logger = logging.getLogger(__name__)


def sync_player_logs() -> int:
    """
    Stub for player logs. The current API key only supports teams, players,
    and games. To avoid runtime errors, this does nothing and returns 0.
    """
    logger.info(
        "sync_player_logs called, but current API key does not support "
        "WNBA per-player game logs. Skipping."
    )
    return 0
