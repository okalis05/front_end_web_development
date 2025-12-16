
from django.contrib import admin
from mystics_site.models import Team, Player, Game, PlayerStat, TeamStat



# Register your models here.
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("full_name", "abbreviation", "conference", "primary_hex", "secondary_hex")
    search_fields = ("full_name", "abbreviation", "city", "name")

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "team", "position_abbreviation", "jersey_number")
    search_fields = ("first_name", "last_name", "college")
    list_filter = ("team",)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("season", "date_utc", "visitor_team", "home_team", "away_score", "home_score", "postseason")
    list_filter = ("season", "postseason", "status")

admin.site.register(PlayerStat)
admin.site.register(TeamStat)
