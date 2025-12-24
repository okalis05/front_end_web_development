from __future__ import annotations

import time

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from mystics_site.models import Team, Player, Game, PlayerStat
from mystics_site.services import get_json, paged, APIError


class Command(BaseCommand):
    help = "Sync WNBA teams, players, games, and SAFE Mystics-only stats (BALLDONTLIE)."

    def add_arguments(self, parser):
        parser.add_argument("--season", type=int, default=2025)

        parser.add_argument("--no-teams", action="store_true", default=False)
        parser.add_argument("--no-players", action="store_true", default=False)
        parser.add_argument("--no-games", action="store_true", default=False)
        parser.add_argument("--no-stats", action="store_true", default=False)

    def handle(self, *args, **opts):
        season = opts["season"]

        do_teams = not opts["no_teams"]
        do_players = not opts["no_players"]
        do_games = not opts["no_games"]
        do_stats = not opts["no_stats"]

        try:
            # --------------------
            # TEAMS
            # --------------------
            if do_teams:
                self.stdout.write("Syncing teams…")
                payload = get_json("/teams")
                for t in payload.get("data", []):
                    Team.objects.update_or_create(
                        api_id=t["id"],
                        defaults={
                            "conference": t.get("conference") or "",
                            "city": t.get("city") or "",
                            "name": t.get("name") or "",
                            "full_name": t.get("full_name") or "",
                            "abbreviation": t.get("abbreviation") or "",
                        },
                    )
                self.stdout.write(self.style.SUCCESS("Teams synced."))

            # --------------------
            # PLAYERS
            # --------------------
            if do_players:
                self.stdout.write("Syncing active players…")
                team_map = {t.api_id: t for t in Team.objects.all()}

                for p in paged("/players", params={"active": "true"}, per_page=25):
                    team = None
                    tid = (p.get("team") or {}).get("id")
                    if tid:
                        team = team_map.get(tid) or Team.objects.filter(api_id=tid).first()
                        if team:
                            team_map[tid] = team

                    Player.objects.update_or_create(
                        api_id=p["id"],
                        defaults={
                            "team": team,
                            "first_name": p.get("first_name") or "",
                            "last_name": p.get("last_name") or "",
                            "position": p.get("position") or "",
                            "position_abbreviation": p.get("position_abbreviation") or "",
                            "height": p.get("height") or "",
                            "weight": p.get("weight") or "",
                            "jersey_number": p.get("jersey_number") or "",
                            "college": p.get("college") or "",
                            "age": p.get("age"),
                            "headshot_url": p.get("headshot_url") or "",
                        },
                    )

                    time.sleep(0.25)

                self.stdout.write(self.style.SUCCESS("Players synced."))

            # --------------------
            # GAMES
            # --------------------
            if do_games:
                self.stdout.write(f"Syncing games for season {season}…")
                team_map = {t.api_id: t for t in Team.objects.all()}

                for g in paged("/games", params={"seasons[]": season}, per_page=25):
                    ht_id = (g.get("home_team") or {}).get("id")
                    vt_id = (g.get("visitor_team") or {}).get("id")
                    if not ht_id or not vt_id:
                        continue

                    ht = team_map.get(ht_id)
                    vt = team_map.get(vt_id)
                    if not ht or not vt:
                        continue

                    home_score = (
                        g.get("home_score")
                        if g.get("home_score") is not None
                        else g.get("home_team_score")
                    )
                    away_score = (
                        g.get("away_score")
                        if g.get("away_score") is not None
                        else g.get("visitor_score")
                        if g.get("visitor_score") is not None
                        else g.get("visitor_team_score")
                    )

                    Game.objects.update_or_create(
                        api_id=g["id"],
                        defaults={
                            "date_utc": parse_datetime(g.get("date") or ""),
                            "season": g.get("season") or season,
                            "postseason": bool(g.get("postseason")),
                            "status": g.get("status") or "",
                            "period": g.get("period"),
                            "time": g.get("time") or "",
                            "home_team": ht,
                            "visitor_team": vt,
                            "home_score": home_score,
                            "away_score": away_score,
                        },
                    )

                    time.sleep(0.25)

                self.stdout.write(self.style.SUCCESS("Games synced."))

            # --------------------
            # SAFE MYSTICS-ONLY PLAYER STATS
            # --------------------
            if do_stats:
                self.stdout.write(f"Syncing Mystics-only player stats for {season}…")

                mystics = Team.objects.filter(full_name="Washington Mystics").first() or Team.objects.filter(
                    full_name__icontains="Mystics"
                ).first()

                if not mystics:
                    self.stdout.write(self.style.ERROR("Mystics team not found."))
                    return

                games = (
                    Game.objects.filter(season=season, home_team=mystics)
                    | Game.objects.filter(season=season, visitor_team=mystics)
                )

                game_map = {g.api_id: g for g in games}
                team_map = {t.api_id: t for t in Team.objects.all()}
                player_map = {p.api_id: p for p in Player.objects.all()}

                for s in paged("/player_stats", params={"seasons[]": season}, per_page=25):
                    g_id = (s.get("game") or {}).get("id")
                    if g_id not in game_map:
                        continue

                    t_id = (s.get("team") or {}).get("id")
                    p_id = (s.get("player") or {}).get("id")

                    game = game_map.get(g_id)
                    team = team_map.get(t_id)
                    player = player_map.get(p_id)

                    if not game or not team or not player:
                        continue

                    PlayerStat.objects.update_or_create(
                        game=game,
                        team=team,
                        player=player,
                        defaults={
                            "min": s.get("min") or "",
                            "pts": s.get("pts"),
                            "reb": s.get("reb"),
                            "ast": s.get("ast"),
                            "stl": s.get("stl"),
                            "blk": s.get("blk"),
                            "turnover": s.get("turnover") if s.get("turnover") is not None else s.get("turnovers"),
                        },
                    )

                    time.sleep(0.35)

                self.stdout.write(self.style.SUCCESS("Mystics stats synced."))

        except APIError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            raise
