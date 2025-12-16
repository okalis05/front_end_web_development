from django.urls import path
from mystics_site import views

app_name = "mystics_site"

urlpatterns = [
    path("", views.home, name="home"),
    path("teams/", views.teams, name="teams"),
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),
    path("players/", views.players, name="players"),
    path("players/<int:player_id>/", views.player_detail, name="player_detail"),

    # JSON for charts (fast + cacheable)
    path("api/player/<int:player_id>/splits/", views.api_player_splits, name="api_player_splits"),
    path("api/team/<int:team_id>/trend/", views.api_team_trend, name="api_team_trend"),
]
