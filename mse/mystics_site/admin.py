from __future__ import annotations

from django.contrib import admin

from mystics_site.models import Team, Player, Game, PlayerStat, TeamStat


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("full_name", "abbreviation", "conference", "primary_hex", "secondary_hex")
    search_fields = ("full_name", "abbreviation", "city", "name")
    list_filter = ("conference",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "team", "position_abbreviation", "jersey_number", "college")
    search_fields = ("first_name", "last_name", "college")
    list_filter = ("team", "position_abbreviation")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("season", "date_utc", "visitor_team", "home_team", "away_score", "home_score", "postseason", "status")
    list_filter = ("season", "postseason", "status")
    search_fields = ("visitor_team__full_name", "home_team__full_name")


@admin.register(PlayerStat)
class PlayerStatAdmin(admin.ModelAdmin):
    list_display = ("game", "player", "team", "pts", "reb", "ast", "stl", "blk")
    list_filter = ("team", "game__season")
    search_fields = ("player__first_name", "player__last_name")


@admin.register(TeamStat)
class TeamStatAdmin(admin.ModelAdmin):
    list_display = ("game", "team", "fgm", "fg3m", "ftm", "reb", "ast", "stl", "blk")
    list_filter = ("team", "game__season")
