# analytics/management/commands/sync_data.py
from django.core.management.base import BaseCommand

from analytics.services.sync_teams import sync_teams
from analytics.services.sync_players import sync_players
from analytics.services.sync_player_logs import sync_player_logs


class Command(BaseCommand):
    help = "Sync WNBA teams, players, and (stub) player logs."

    def handle(self, *args, **kwargs):
        self.stdout.write("Syncing TEAMS...")
        sync_teams()

        self.stdout.write("Syncing PLAYERS...")
        sync_players()

        self.stdout.write("Syncing PLAYER LOGS (stub)...")
        sync_player_logs()

        self.stdout.write(self.style.SUCCESS("Sync completed."))
