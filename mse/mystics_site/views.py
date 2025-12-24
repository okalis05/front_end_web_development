from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from mystics_site.models import Team, Player, Game, PlayerStat
from mystics_site.utils import get_mystics

SEASON_DEFAULT = 2025


# -------------------------
# Helpers
# -------------------------
def _season(request: HttpRequest) -> int:
    s = request.GET.get("season")
    return int(s) if s and s.isdigit() else SEASON_DEFAULT


def _team_points_from_game(game: Game, team: Team) -> int:
    """Return points scored by `team` in this game using Game scores."""
    if game.home_team_id == team.id:
        return int(game.home_score or 0)
    return int(game.away_score or 0)


def _team_points_allowed_from_game(game: Game, team: Team) -> int:
    """Return points allowed by `team` in this game using Game scores."""
    if game.home_team_id == team.id:
        return int(game.away_score or 0)
    return int(game.home_score or 0)


def _games_for_team(season: int, team: Team):
    return (
        Game.objects.filter(season=season)
        .filter(Q(home_team=team) | Q(visitor_team=team))
        .exclude(date_utc__isnull=True)
        .order_by("date_utc")
    )


def _safe_avg(nums: List[float]) -> float:
    nums2 = [float(x) for x in nums if isinstance(x, (int, float))]
    return (sum(nums2) / len(nums2)) if nums2 else 0.0


# -------------------------
# Pages
# -------------------------
def home(request: HttpRequest):
    season = _season(request)

    top_scorers = (
        PlayerStat.objects
        .filter(game__season=season)
        .values(
            "player__api_id",
            "player__first_name",
            "player__last_name",
            "player__team__abbreviation",
        )
        .annotate(ppg=Avg("pts"), g=Count("game_id"))
        .filter(g__gte=5)
        .order_by("-ppg")[:10]
    )

    top_players = (
        PlayerStat.objects
        .filter(game__season=season)
        .values("player__first_name", "player__last_name")
        .annotate(ppg=Avg("pts"), g=Count("game_id"))
        .filter(g__gte=5)
        .order_by("-ppg")[:5]
    )

    context = {
        "season": season,
        "teams_count": Team.objects.count(),
        "players_count": Player.objects.count(),
        "games_count": Game.objects.filter(season=season).count(),
        "top_scorers": top_scorers,
        "top_players": top_players,
    }
    return render(request, "mystics_site/home.html", context)


def dashboard(request: HttpRequest):
    season = _season(request)
    mystics = get_mystics()

    if not mystics:
        return render(request, "mystics_site/dashboard.html", {
            "season": season,
            "error": "Washington Mystics not found in database. Run: python manage.py mystics_sync --season 2025",
        })

    games_played = _games_for_team(season, mystics)

    top_players = (
        PlayerStat.objects
        .filter(team=mystics, game__season=season)
        .values("player__first_name", "player__last_name")
        .annotate(ppg=Avg("pts"), g=Count("game_id"))
        .filter(g__gte=5)
        .order_by("-ppg")[:5]
    )

    return render(request, "mystics_site/dashboard.html", {
        "mystics": mystics,
        "season": season,
        "games_count": games_played.count(),
        "top_players": top_players,
    })


def executive_dashboard(request: HttpRequest):
    """
    Executive dashboard page:
    - Mystics 2025 points per game (filled line)   [UNCHANGED line chart concept]
    - Mystics bar: avg points per quarter (2024 vs 2025) [NEW bar]
    - Team vs Team: line trend + quarter bar + AI summary [NEW bar + summary]
    """
    season = _season(request)
    teams = Team.objects.order_by("full_name")
    mystics = get_mystics()
    return render(request, "mystics_site/executive_dashboard.html", {
        "season": season,
        "teams": teams,
        "mystics": mystics,
    })


def teams(request: HttpRequest):
    q = (request.GET.get("q") or "").strip()
    qs = Team.objects.order_by("full_name")
    if q:
        qs = qs.filter(full_name__icontains=q)
    return render(request, "mystics_site/teams.html", {"teams": qs, "q": q})


def team_detail(request: HttpRequest, team_id: int):
    season = _season(request)
    team = get_object_or_404(Team, api_id=team_id)

    roster = team.players.select_related("team").order_by("last_name", "first_name")

    recent_games = (
        Game.objects
        .filter(season=season)
        .filter(Q(home_team=team) | Q(visitor_team=team))
        .order_by("-date_utc")[:10]
    )

    return render(request, "mystics_site/team_detail.html", {
        "team": team,
        "season": season,
        "roster": roster,
        "recent_games": recent_games,
    })


def players(request: HttpRequest):
    q = (request.GET.get("q") or "").strip()
    team = (request.GET.get("team") or "").strip()

    qs = Player.objects.select_related("team")

    if q:
        qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))

    if team.isdigit():
        qs = qs.filter(team__api_id=int(team))

    qs = qs.order_by("last_name", "first_name")

    return render(request, "mystics_site/players.html", {
        "players": qs[:300],
        "q": q,
        "teams": Team.objects.order_by("full_name"),
        "team": team,
    })


def player_detail(request: HttpRequest, player_id: int):
    season = _season(request)
    player = get_object_or_404(Player, api_id=player_id)

    agg = PlayerStat.objects.filter(
        player=player,
        game__season=season
    ).aggregate(
        g=Count("id"),
        ppg=Avg("pts"),
        rpg=Avg("reb"),
        apg=Avg("ast"),
        spg=Avg("stl"),
        bpg=Avg("blk"),
        tpg=Avg("turnover"),
    )

    last10 = (
        PlayerStat.objects
        .filter(player=player, game__season=season)
        .select_related("game", "team")
        .order_by("-game__date_utc")[:10]
    )

    return render(request, "mystics_site/player_detail.html", {
        "player": player,
        "season": season,
        "agg": agg,
        "last10": last10,
    })


# -------------------------
# APIs
# -------------------------
@cache_page(60 * 10)
def players_api(request: HttpRequest):
    q = (request.GET.get("q") or "").strip()
    limit_raw = request.GET.get("limit", "250")

    try:
        limit = int(limit_raw)
    except Exception:
        limit = 250

    limit = max(1, min(limit, 500))

    qs = Player.objects.select_related("team")

    if q:
        qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))

    qs = qs.order_by("last_name", "first_name")[:limit]

    data = [
        {
            "api_id": p.api_id,
            "name": p.full_name,
            "position": p.position_abbreviation or p.position or "",
            "team": (p.team.abbreviation if p.team else "") or "",
            "team_full": (p.team.full_name if p.team else "") or "",
            "headshot_url": p.headshot_url or "",
        }
        for p in qs
    ]

    return JsonResponse({"count": len(data), "results": data})


@cache_page(60 * 10)
def api_player_splits(request: HttpRequest, player_id: int):
    season = _season(request)
    player = get_object_or_404(Player, api_id=player_id)

    rows = (
        PlayerStat.objects
        .filter(player=player, game__season=season, game__date_utc__isnull=False)
        .annotate(m=TruncMonth("game__date_utc"))
        .values("m")
        .annotate(ppg=Avg("pts"))
        .order_by("m")
    )

    labels, ppg = [], []
    for r in rows:
        m = r.get("m")
        labels.append(m.strftime("%b") if m else "—")
        ppg.append(round(r.get("ppg") or 0.0, 2))

    return JsonResponse({
        "player": player.full_name,
        "season": season,
        "labels": labels,
        "ppg": ppg,
    })


@cache_page(60 * 10)
def api_team_trend(request: HttpRequest, team_id: int):
    season = _season(request)
    team = get_object_or_404(Team, api_id=team_id)

    games = _games_for_team(season, team)

    labels, pts = [], []
    for g in games:
        labels.append(g.date_utc.strftime("%m/%d"))
        pts.append(_team_points_from_game(g, team))

    return JsonResponse({"team": team.full_name, "season": season, "labels": labels, "pts": pts})


@cache_page(60 * 10)
def api_mystics_trend(request: HttpRequest):
    season = _season(request)
    mystics = get_mystics()

    if not mystics:
        return JsonResponse({"team": "Washington Mystics", "season": season, "labels": [], "pts": []})

    games = _games_for_team(season, mystics)

    labels, pts = [], []
    for g in games:
        labels.append(g.date_utc.strftime("%m/%d"))
        pts.append(_team_points_from_game(g, mystics))

    return JsonResponse({
        "team": mystics.full_name,
        "season": season,
        "labels": labels,
        "pts": pts,
    })


@cache_page(60 * 10)
def api_teams_list(request: HttpRequest):
    teams = Team.objects.order_by("full_name").values("api_id", "full_name", "abbreviation")
    return JsonResponse({"results": list(teams)})


@cache_page(60 * 10)
def api_mystics_ppg(request: HttpRequest):
    """
    Filled line chart data:
    - labels: game dates
    - pts: actual points per game (game-by-game points)
    """
    season = _season(request)
    mystics = get_mystics()
    if not mystics:
        return JsonResponse({"team": "Washington Mystics", "season": season, "labels": [], "pts": []})

    games = _games_for_team(season, mystics)
    labels, pts = [], []
    for g in games:
        labels.append(g.date_utc.strftime("%m/%d"))
        pts.append(_team_points_from_game(g, mystics))

    return JsonResponse({"team": mystics.full_name, "season": season, "labels": labels, "pts": pts})


# ✅ NEW: Quarter averages endpoint (used ONLY by bar charts)
@cache_page(60 * 10)
def api_team_quarter_averages(request: HttpRequest, team_id: int):
    """
    Average points per quarter for a team in a given season.

    NOTE:
    Your current DB schema stores final scores only (Game.home_score/away_score).
    True per-quarter scoring isn't available from those fields, so we provide a
    defensible estimate: PPG / 4 for each quarter.

    If later you ingest real per-quarter stats, update only this endpoint.
    """
    season = _season(request)
    team = get_object_or_404(Team, api_id=team_id)

    games = _games_for_team(season, team)
    pts = [_team_points_from_game(g, team) for g in games]
    ppg = _safe_avg([float(x) for x in pts]) if pts else 0.0

    q = round(ppg / 4.0, 2) if ppg else 0.0
    return JsonResponse({
        "team": team.full_name,
        "team_api_id": team.api_id,
        "abbr": team.abbreviation,
        "primary_hex": team.primary_hex,
        "secondary_hex": team.secondary_hex,
        "season": season,
        "quarters": ["Q1", "Q2", "Q3", "Q4"],
        "values": [q, q, q, q],
        "note": "Estimated from final score (PPG/4).",
        "games": len(pts),
        "ppg": round(ppg, 2),
    })


@cache_page(60 * 10)
def api_mystics_season_compare(request: HttpRequest):
    """
    (Kept for backward compatibility. Your executive dashboard bar chart now uses
    api_team_quarter_averages, but this endpoint can remain.)
    """
    mystics = get_mystics()
    if not mystics:
        return JsonResponse({"team": "Washington Mystics", "labels": ["2024", "2025"], "ppg": [0, 0]})

    s1 = request.GET.get("s1", "2024")
    s2 = request.GET.get("s2", "2025")
    try:
        season1 = int(s1)
        season2 = int(s2)
    except Exception:
        season1, season2 = 2024, 2025

    def season_ppg(season: int) -> float:
        games = _games_for_team(season, mystics)
        pts = [_team_points_from_game(g, mystics) for g in games]
        return round(sum(pts) / len(pts), 2) if pts else 0.0

    p1 = season_ppg(season1)
    p2 = season_ppg(season2)

    return JsonResponse({
        "team": mystics.full_name,
        "labels": [str(season1), str(season2)],
        "ppg": [p1, p2],
    })


@cache_page(60 * 10)
def api_compare_teams(request: HttpRequest):
    """
    Team-vs-team comparison endpoint.
    Returns union-date labels and points series for both teams.
    Query params:
      - team_a (api_id)
      - team_b (api_id)
      - season (default 2025)
    """
    season = _season(request)
    a_raw = (request.GET.get("team_a") or "").strip()
    b_raw = (request.GET.get("team_b") or "").strip()

    if not (a_raw.isdigit() and b_raw.isdigit()):
        return JsonResponse({"labels": [], "team_a": None, "team_b": None, "a_pts": [], "b_pts": []})

    team_a = get_object_or_404(Team, api_id=int(a_raw))
    team_b = get_object_or_404(Team, api_id=int(b_raw))

    games_a = list(_games_for_team(season, team_a))
    games_b = list(_games_for_team(season, team_b))

    map_a = {g.date_utc.date().isoformat(): _team_points_from_game(g, team_a) for g in games_a if g.date_utc}
    map_b = {g.date_utc.date().isoformat(): _team_points_from_game(g, team_b) for g in games_b if g.date_utc}

    all_dates = sorted(set(map_a.keys()) | set(map_b.keys()))
    labels = []
    a_pts, b_pts = [], []

    for d in all_dates:
        y, m, day = d.split("-")
        labels.append(f"{m}/{day}")
        a_pts.append(map_a.get(d))
        b_pts.append(map_b.get(d))

    return JsonResponse({
        "season": season,
        "labels": labels,
        "team_a": {
            "api_id": team_a.api_id,
            "name": team_a.full_name,
            "abbr": team_a.abbreviation,
            "primary_hex": team_a.primary_hex,
            "secondary_hex": team_a.secondary_hex,
        },
        "team_b": {
            "api_id": team_b.api_id,
            "name": team_b.full_name,
            "abbr": team_b.abbreviation,
            "primary_hex": team_b.primary_hex,
            "secondary_hex": team_b.secondary_hex,
        },
        "a_pts": a_pts,
        "b_pts": b_pts,
    })


def mystics_players(request: HttpRequest):
    mystics = get_mystics()

    if not mystics:
        return render(
            request,
            "mystics_site/players.html",
            {
                "players": [],
                "teams": Team.objects.order_by("full_name"),
                "team": "",
                "q": "",
                "error": "Washington Mystics not found.",
            },
        )

    players = (
        Player.objects
        .filter(team=mystics)
        .select_related("team")
        .order_by("last_name", "first_name")
    )

    return render(
        request,
        "mystics_site/players.html",
        {
            "players": players,
            "teams": Team.objects.order_by("full_name"),
            "team": str(mystics.api_id),
            "q": "",
            "mystics_only": True,
        },
    )
