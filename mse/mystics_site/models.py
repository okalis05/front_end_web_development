from __future__ import annotations
from django.db import models


class Team(models.Model):
    api_id = models.IntegerField(unique=True, db_index=True)
    conference = models.CharField(max_length=64, blank=True, default="")
    city = models.CharField(max_length=64, blank=True, default="")
    name = models.CharField(max_length=64, blank=True, default="")
    full_name = models.CharField(max_length=128, blank=True, default="")
    abbreviation = models.CharField(max_length=8, blank=True, default="")

    # Cosmetics
    primary_hex = models.CharField(max_length=16, blank=True, default="#1f6fff")
    secondary_hex = models.CharField(max_length=16, blank=True, default="#ff2a3a")

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["conference"]),
            models.Index(fields=["abbreviation"]),
        ]

    def __str__(self) -> str:
        return self.full_name or f"Team {self.api_id}"


class Player(models.Model):
    api_id = models.IntegerField(unique=True, db_index=True)
    team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="players"
    )

    first_name = models.CharField(max_length=64, blank=True, default="")
    last_name = models.CharField(max_length=64, blank=True, default="")
    position = models.CharField(max_length=32, blank=True, default="")
    position_abbreviation = models.CharField(max_length=8, blank=True, default="")
    height = models.CharField(max_length=16, blank=True, default="")
    weight = models.CharField(max_length=16, blank=True, default="")
    jersey_number = models.CharField(max_length=8, blank=True, default="")
    college = models.CharField(max_length=128, blank=True, default="")
    age = models.IntegerField(null=True, blank=True)

    headshot_url = models.URLField(blank=True, default="")

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
        ]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.full_name or f"Player {self.api_id}"


class Game(models.Model):
    api_id = models.IntegerField(unique=True, db_index=True)
    date_utc = models.DateTimeField(null=True, blank=True)
    season = models.IntegerField(db_index=True)
    postseason = models.BooleanField(default=False)
    status = models.CharField(max_length=32, blank=True, default="")
    period = models.IntegerField(null=True, blank=True)
    time = models.CharField(max_length=16, blank=True, default="")

    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_games")
    visitor_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_games")
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-date_utc"]
        indexes = [models.Index(fields=["season", "postseason"])]

    def __str__(self) -> str:
        ht = getattr(self.home_team, "abbreviation", "HOME")
        vt = getattr(self.visitor_team, "abbreviation", "AWAY")
        return f"{self.season} {vt}@{ht}"


class PlayerStat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="player_stats")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="game_stats")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="player_stats")

    min = models.CharField(max_length=8, blank=True, default="")

    fgm = models.IntegerField(null=True, blank=True)
    fga = models.IntegerField(null=True, blank=True)
    fg3m = models.IntegerField(null=True, blank=True)
    fg3a = models.IntegerField(null=True, blank=True)
    ftm = models.IntegerField(null=True, blank=True)
    fta = models.IntegerField(null=True, blank=True)

    oreb = models.IntegerField(null=True, blank=True)
    dreb = models.IntegerField(null=True, blank=True)
    reb = models.IntegerField(null=True, blank=True)
    ast = models.IntegerField(null=True, blank=True)
    stl = models.IntegerField(null=True, blank=True)
    blk = models.IntegerField(null=True, blank=True)
    turnover = models.IntegerField(null=True, blank=True)
    pf = models.IntegerField(null=True, blank=True)
    pts = models.IntegerField(null=True, blank=True)
    plus_minus = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("game", "player", "team")]
        indexes = [
            models.Index(fields=["player"]),
            models.Index(fields=["team"]),
            models.Index(fields=["game"]),
        ]


class TeamStat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="team_stats")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game_team_stats")

    fgm = models.IntegerField(null=True, blank=True)
    fga = models.IntegerField(null=True, blank=True)
    fg_pct = models.FloatField(null=True, blank=True)

    fg3m = models.IntegerField(null=True, blank=True)
    fg3a = models.IntegerField(null=True, blank=True)
    fg3_pct = models.FloatField(null=True, blank=True)

    ftm = models.IntegerField(null=True, blank=True)
    fta = models.IntegerField(null=True, blank=True)
    ft_pct = models.FloatField(null=True, blank=True)

    oreb = models.IntegerField(null=True, blank=True)
    dreb = models.IntegerField(null=True, blank=True)
    reb = models.IntegerField(null=True, blank=True)
    ast = models.IntegerField(null=True, blank=True)
    stl = models.IntegerField(null=True, blank=True)
    blk = models.IntegerField(null=True, blank=True)

    turnovers = models.IntegerField(null=True, blank=True)
    fouls = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("game", "team")]
        indexes = [
            models.Index(fields=["team"]),
            models.Index(fields=["game"]),
        ]
