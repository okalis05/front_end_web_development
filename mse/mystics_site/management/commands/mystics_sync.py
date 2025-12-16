from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime

from mystics_site.models import Team, Player, Game, PlayerStat, TeamStat
from mystics_site.services import get_json, paged

class Command(BaseCommand):
    help = "Sync WNBA teams/players/games + 2025 stats into local DB (BALLDONTLIE)."

    def add_arguments(self, parser):
        parser.add_argument("--season", type=int, default=2025)
        parser.add_argument("--players", action="store_true", default=True)
        parser.add_argument("--teams", action="store_true", default=True)
        parser.add_argument("--games", action="store_true", default=True)
        parser.add_argument("--stats", action="store_true", default=True)

    @transaction.atomic
    def handle(self, *args, **opts):
        season = opts["season"]

        if opts["teams"]:
            self.stdout.write("Syncing teams…")
            payload = get_json("/teams")
            for t in payload.get("data", []):
                Team.objects.update_or_create(
                    api_id=t["id"],
                    defaults=dict(
                        conference=t.get("conference") or "",
                        city=t.get("city") or "",
                        name=t.get("name") or "",
                        full_name=t.get("full_name") or "",
                        abbreviation=t.get("abbreviation") or "",
                    ),
                )
            self.stdout.write(self.style.SUCCESS("Teams synced."))

        if opts["players"]:
            self.stdout.write("Syncing active players…")
            for p in paged("/players", params={"active": "true"}):
                team = None
                if p.get("team") and p["team"].get("id"):
                    team = Team.objects.filter(api_id=p["team"]["id"]).first()
                Player.objects.update_or_create(
                    api_id=p["id"],
                    defaults=dict(
                        team=team,
                        first_name=p.get("first_name") or "",
                        last_name=p.get("last_name") or "",
                        position=p.get("position") or "",
                        position_abbreviation=p.get("position_abbreviation") or "",
                        height=p.get("height") or "",
                        weight=p.get("weight") or "",
                        jersey_number=p.get("jersey_number") or "",
                        college=p.get("college") or "",
                        age=p.get("age"),
                    ),
                )
            self.stdout.write(self.style.SUCCESS("Players synced."))

        if opts["games"]:
            self.stdout.write(f"Syncing games for season {season}…")
            for g in paged("/games", params={"seasons[]": season}):
                ht = Team.objects.get(api_id=g["home_team"]["id"])
                vt = Team.objects.get(api_id=g["visitor_team"]["id"])
                Game.objects.update_or_create(
                    api_id=g["id"],
                    defaults=dict(
                        date_utc=parse_datetime(g.get("date") or ""),
                        season=g.get("season") or season,
                        postseason=bool(g.get("postseason")),
                        status=g.get("status") or "",
                        period=g.get("period"),
                        time=g.get("time") or "",
                        home_team=ht,
                        visitor_team=vt,
                        home_score=g.get("home_score"),
                        away_score=g.get("away_score"),
                    ),
                )
            self.stdout.write(self.style.SUCCESS("Games synced."))

        if opts["stats"]:
            self.stdout.write(f"Syncing player_stats for season {season}… (this can be large)")
            # Player stats
            for s in paged("/player_stats", params={"seasons[]": season}):
                game = Game.objects.filter(api_id=s["game"]["id"]).first()
                if not game:
                    continue
                team = Team.objects.filter(api_id=s["team"]["id"]).first()
                player = Player.objects.filter(api_id=s["player"]["id"]).first()
                if not team or not player:
                    continue
                PlayerStat.objects.update_or_create(
                    game=game, team=team, player=player,
                    defaults=dict(
                        min=s.get("min") or "",
                        fgm=s.get("fgm"), fga=s.get("fga"),
                        fg3m=s.get("fg3m"), fg3a=s.get("fg3a"),
                        ftm=s.get("ftm"), fta=s.get("fta"),
                        oreb=s.get("oreb"), dreb=s.get("dreb"),
                        reb=s.get("reb"), ast=s.get("ast"),
                        stl=s.get("stl"), blk=s.get("blk"),
                        turnover=s.get("turnover"), pf=s.get("pf"),
                        pts=s.get("pts"), plus_minus=s.get("plus_minus"),
                    )
                )

            self.stdout.write(f"Syncing team_stats for season {season}…")
            for s in paged("/team_stats", params={"seasons[]": season}):
                game = Game.objects.filter(api_id=s["game"]["id"]).first()
                if not game:
                    continue
                team = Team.objects.filter(api_id=s["team"]["id"]).first()
                if not team:
                    continue
                TeamStat.objects.update_or_create(
                    game=game, team=team,
                    defaults=dict(
                        fgm=s.get("fgm"), fga=s.get("fga"), fg_pct=s.get("fg_pct"),
                        fg3m=s.get("fg3m"), fg3a=s.get("fg3a"), fg3_pct=s.get("fg3_pct"),
                        ftm=s.get("ftm"), fta=s.get("fta"), ft_pct=s.get("ft_pct"),
                        oreb=s.get("oreb"), dreb=s.get("dreb"), reb=s.get("reb"),
                        ast=s.get("ast"), stl=s.get("stl"), blk=s.get("blk"),
                        turnovers=s.get("turnovers"), fouls=s.get("fouls"),
                    )
                )

            self.stdout.write(self.style.SUCCESS("Stats synced."))
