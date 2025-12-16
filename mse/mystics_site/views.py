
from __future__ import annotations

from django.shortcuts import render
from django.db.models import Avg, Sum, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from mystics_site.models import Team, Player, Game, PlayerStat, TeamStat
# Create your views here.
def home(request):
    season = 2025
    teams_count = Team.objects.count()
    players_count = Player.objects.count()
    games_count = Game.objects.filter(season=season).count()

    top_scorers = (
        PlayerStat.objects.filter(game__season=season)
        .values("player_id", "player__first_name", "player__last_name", "player__team__abbreviation")
        .annotate(ppg=Avg("pts"), g=Count("game_id"))
        .filter(g__gte=5)
        .order_by("-ppg")[:10]
    )

    return render(request, "mystics_site/home.html", {
        "season": season,
        "teams_count": teams_count,
        "players_count": players_count,
        "games_count": games_count,
        "top_scorers": top_scorers,
    })

def teams(request):
    q = (request.GET.get("q") or "").strip()
    qs = Team.objects.all().order_by("full_name")
    if q:
        qs = qs.filter(full_name__icontains=q)
    return render(request, "mystics_site/teams.html", {"teams": qs, "q": q})

def team_detail(request, team_id: int):
    team = get_object_or_404(Team, api_id=team_id)
    roster = team.players.all().order_by("last_name", "first_name")
    recent_games = (
        Game.objects.filter(season=2025)
        .filter(home_team=team) | Game.objects.filter(season=2025, visitor_team=team)
    )
    recent_games = recent_games.order_by("-date_utc")[:10]
    return render(request, "mystics_site/team_detail.html", {
        "team": team, "roster": roster, "recent_games": recent_games
    })

def players(request):
    q = (request.GET.get("q") or "").strip()
    team = request.GET.get("team") or ""
    qs = Player.objects.select_related("team").all().order_by("last_name", "first_name")
    if q:
        qs = qs.filter(last_name__icontains=q) | qs.filter(first_name__icontains=q)
    if team.isdigit():
        qs = qs.filter(team__api_id=int(team))
    teams = Team.objects.all().order_by("full_name")
    return render(request, "mystics_site/players.html", {"players": qs[:250], "q": q, "teams": teams, "team": team})

def player_detail(request, player_id: int):
    player = get_object_or_404(Player, api_id=player_id)
    season = 2025

    # simple season aggregates from game stats
    agg = (
        PlayerStat.objects.filter(player=player, game__season=season)
        .aggregate(
            g=Count("id"),
            ppg=Avg("pts"),
            rpg=Avg("reb"),
            apg=Avg("ast"),
            spg=Avg("stl"),
            bpg=Avg("blk"),
            tpg=Avg("turnover"),
        )
    )

    last10 = (
        PlayerStat.objects.filter(player=player, game__season=season)
        .select_related("game", "team")
        .order_by("-game__date_utc")[:10]
    )

    return render(request, "mystics_site/player_detail.html", {
        "player": player,
        "season": season,
        "agg": agg,
        "last10": last10,
    })

@cache_page(60 * 10)
def api_player_splits(request, player_id: int):
    player = get_object_or_404(Player, api_id=player_id)
    season = 2025

    # PTS by month (sparkline/bar)
    rows = (
        PlayerStat.objects.filter(player=player, game__season=season, game__date_utc__isnull=False)
        .extra(select={"month": "strftime('%%m', date_utc)"})  # works on SQLite
        .values("month")
        .annotate(ppg=Avg("pts"), g=Count("id"))
        .order_by("month")
    )
    labels = [r["month"] for r in rows]
    ppg = [round((r["ppg"] or 0), 2) for r in rows]

    return JsonResponse({
        "player": player.full_name,
        "season": season,
        "labels": labels,
        "ppg": ppg,
    })

@cache_page(60 * 10)
def api_team_trend(request, team_id: int):
    team = get_object_or_404(Team, api_id=team_id)
    season = 2025

    # Team points by game date (line)
    qs = (
        TeamStat.objects.filter(team=team, game__season=season, game__date_utc__isnull=False)
        .select_related("game")
        .order_by("game__date_utc")
    )
    labels = []
    pts = []
    for row in qs:
        # approximate points as: FGM*2 + FG3M + FTM (common calc; WNBA has 2/3/FT)
        labels.append(row.game.date_utc.strftime("%m/%d"))
        p = (row.fgm or 0) * 2 + (row.fg3m or 0) + (row.ftm or 0)
        pts.append(int(p))

    return JsonResponse({"team": team.full_name, "season": season, "labels": labels, "pts": pts})
