# analytics/management/commands/sync_all.py
from django.core.management.base import BaseCommand

from analytics.services.sync_teams import sync_teams
from analytics.services.sync_players import sync_players
from analytics.services.sync_games import sync_games
from analytics.services.season_averages import sync_season_averages


class Command(BaseCommand):
    help = "Sync WNBA data (teams, players, games) from BallDontLie (WNBA)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--season",
            type=int,
            default=2024,
            help="Season year to sync games for (e.g. 2024, 2025).",
        )

    def handle(self, *args, **options):
        season = options["season"]

        self.stdout.write(self.style.MIGRATE_HEADING(f"Syncing WNBA data for {season}"))

        self.stdout.write("Syncing teams…")
        t = sync_teams()
        self.stdout.write(self.style.SUCCESS(f"Teams synced: {t}"))

        self.stdout.write("Syncing players…")
        p = sync_players()
        self.stdout.write(self.style.SUCCESS(f"Players synced: {p}"))

        self.stdout.write(f"Syncing games for {season}…")
        g = sync_games(season=season)
        self.stdout.write(self.style.SUCCESS(f"Games synced: {g}"))

        self.stdout.write("Syncing season averages (stub)…")
        sa = sync_season_averages(season=season)
        if sa:
            self.stdout.write(self.style.SUCCESS(f"Season averages synced: {sa}"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Season averages skipped – not available with this API key."
                )
            )

        self.stdout.write(self.style.SUCCESS("ALL DATA SYNCED!"))
