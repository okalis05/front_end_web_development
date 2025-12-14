# analytics/urls.py
from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.index, name="index"),
    path("roster/", views.roster, name="roster"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("league/", views.league_dashboard, name="league_dashboard"),
    path("player/<int:player_id>/", views.player_detail, name="player_detail"),
    path(
        "api/player/<int:player_id>/game-log/",
        views.player_game_log_api,
        name="player_game_log",
    ),
    path("teams/", views.teams, name="teams"),
    path("games/", views.games, name="games"),
    path("stats/", views.stats, name="stats"),
]


