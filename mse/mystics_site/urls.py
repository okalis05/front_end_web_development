from __future__ import annotations

from django.urls import path
from mystics_site import views

app_name = "mystics_site"

urlpatterns = [
    # Pages
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("executive-dashboard/", views.executive_dashboard, name="executive_dashboard"),

    path("teams/", views.teams, name="teams"),
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),

    path("players/", views.players, name="players"),
    path("players/<int:player_id>/", views.player_detail, name="player_detail"),

    # APIs
    path("api/players/", views.players_api, name="players_api"),
    path("api/player/<int:player_id>/splits/", views.api_player_splits, name="api_player_splits"),

    path("api/team/<int:team_id>/trend/", views.api_team_trend, name="api_team_trend"),
    path("api/mystics/trend/", views.api_mystics_trend, name="api_mystics_trend"),

    # Executive dashboard APIs
    path("api/teams/list/", views.api_teams_list, name="api_teams_list"),
    path("api/mystics/ppg/", views.api_mystics_ppg, name="api_mystics_ppg"),
    path("api/mystics/season-compare/", views.api_mystics_season_compare, name="api_mystics_season_compare"),
    path("api/compare/teams/", views.api_compare_teams, name="api_compare_teams"),

    path("api/team/<int:team_id>/quarters/", views.api_team_quarter_averages, name="api_team_quarter_averages"),

    # Convenience page
    path("mystics/players/", views.mystics_players, name="mystics_players"),
]
