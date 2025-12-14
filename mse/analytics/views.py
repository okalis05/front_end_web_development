# analytics/views.py
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Player, PlayerGameStat, Team, TeamSeasonStat

# You can change this to whatever season you're targeting
SEASON_DEFAULT = 2025


def index(request):
    """
    Home page hero + quick season overview.
    """
    season = SEASON_DEFAULT
    team = Team.objects.filter(name__icontains="Mystics").first()
    team_stats = None
    league_avg_ppg = None

    if team:
        team_stats = TeamSeasonStat.objects.filter(team=team, season=season).first()
        league_qs = TeamSeasonStat.objects.filter(season=season)
        league_avg_ppg = league_qs.aggregate(Avg("ppg"))["ppg__avg"]

    context = {
        "team": team,
        "team_stats": team_stats,
        "league_avg_ppg": league_avg_ppg,
        "season": season,
    }
    return render(request, "analytics/index.html", context)


def roster(request):
    """
    Roster explorer – pulls live Mystics players from DB.
    """
    team = Team.objects.filter(name__icontains="Mystics").first()
    players = Player.objects.filter(team=team).order_by("last_name") if team else []
    return render(
        request,
        "analytics/roster.html",
        {"players": players, "team": team},
    )


def dashboard(request):
    """
    Mystics team dashboard – scoring, rebounding, passing vs league averages.
    """
    season = SEASON_DEFAULT
    team = Team.objects.filter(name__icontains="Mystics").first()
    team_stats = None
    league_avg_ppg = league_avg_rpg = league_avg_apg = None

    if team:
        team_stats = TeamSeasonStat.objects.filter(team=team, season=season).first()
        league_qs = TeamSeasonStat.objects.filter(season=season)
        agg = league_qs.aggregate(
            avg_ppg=Avg("ppg"),
            avg_rpg=Avg("rpg"),
            avg_apg=Avg("apg"),
        )
        league_avg_ppg = agg["avg_ppg"]
        league_avg_rpg = agg["avg_rpg"]
        league_avg_apg = agg["avg_apg"]

    context = {
        "team": team,
        "team_stats": team_stats,
        "league_avg_ppg": league_avg_ppg,
        "league_avg_rpg": league_avg_rpg,
        "league_avg_apg": league_avg_apg,
        "season": season,
    }
    return render(request, "analytics/dashboard.html", context)


def league_dashboard(request):
    """
    League-wide team table sorted by PPG.
    """
    season = SEASON_DEFAULT
    teams_stats = (
        TeamSeasonStat.objects.filter(season=season)
        .select_related("team")
        .order_by("-ppg")
    )
    return render(
        request,
        "analytics/league_dashboard.html",
        {"teams_stats": teams_stats, "season": season},
    )


def player_detail(request, player_id: int):
    """
    Single player page with headshot + summary + chart container.
    """
    player = get_object_or_404(Player, pk=player_id)
    game_stats = player.game_stats.all().order_by("game_date")
    return render(
        request,
        "analytics/player_detail.html",
        {
            "player": player,
            "game_stats": game_stats,
            "season": SEASON_DEFAULT,
        },
    )


def player_game_log_api(request, player_id: int):
    """
    JSON API for the front-end Chart.js line chart (points per game).
    """
    player = get_object_or_404(Player, pk=player_id)
    logs = list(player.game_stats.all().order_by("game_date"))
    data = {
        "player": str(player),
        "games": [
            {
                "date": g.game_date.isoformat(),
                "points": g.points,
                "rebounds": g.rebounds,
                "assists": g.assists,
                "minutes": g.minutes,
                "opponent": g.opponent,
            }
            for g in logs
        ],
    }
    return JsonResponse(data)


def stats(request):
    """
    Demo charts page – uses the same visuals but not tied to extra endpoints yet.
    """
    return render(
        request,
        "analytics/stats.html",
        {"season": SEASON_DEFAULT},
    )


def teams(request):
    """
    Optional teams page – just show the league table again grouped by conference.
    """
    season = SEASON_DEFAULT
    teams_stats = (
        TeamSeasonStat.objects.filter(season=season)
        .select_related("team")
        .order_by("team__conference", "team__city")
    )
    return render(
        request,
        "analytics/teams.html",
        {"teams_stats": teams_stats, "season": season},
    )


def games(request):
    """
    Stub page (you can wire Game model + schedule later).
    """
    return render(request, "analytics/games.html", {"season": SEASON_DEFAULT})
