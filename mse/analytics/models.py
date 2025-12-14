from django.db import models


class Team(models.Model):
    """
    Basketball team (NBA or WNBA).
    external_id is the ID from the external API (BallDontLie / WNBA).
    """
    external_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10)
    conference = models.CharField(max_length=50, blank=True)
    division = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return self.full_name or f"{self.city} {self.name}"


class Player(models.Model):
    """
    Player linked to a Team, with optional bio/headshot info.
    """
    external_id = models.CharField(max_length=64, unique=True)  # API player ID
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players",
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    jersey = models.CharField(max_length=10, blank=True)
    position = models.CharField(max_length=20, blank=True)
    height = models.CharField(max_length=20, blank=True)
    weight = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    headshot_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class TeamSeasonStat(models.Model):
    """
    Optional roll-up stats for a team by season (can be computed from game data).
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.IntegerField()
    ppg = models.FloatField(null=True, blank=True)     # points per game
    rpg = models.FloatField(null=True, blank=True)     # rebounds
    apg = models.FloatField(null=True, blank=True)     # assists
    net_rating = models.FloatField(null=True, blank=True)
    off_rating = models.FloatField(null=True, blank=True)
    def_rating = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("team", "season")

    def __str__(self) -> str:
        return f"{self.team} – {self.season}"

class Game(models.Model):
    external_id = models.IntegerField(unique=True)
    date = models.DateTimeField()
    home_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="home_games")
    visitor_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="visitor_games")
    home_team_score = models.IntegerField(null=True, blank=True)
    visitor_team_score = models.IntegerField(null=True, blank=True)
    season = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.home_team} vs {self.visitor_team} ({self.date.date()})"



class SeasonAverage(models.Model):
    """
    Per-season per-player stats from BallDontLie /season_averages endpoint.
    """
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="season_averages",
    )
    season = models.IntegerField()

    games_played = models.IntegerField(default=0)
    minutes = models.CharField(max_length=10, blank=True)

    points = models.FloatField(default=0)
    rebounds = models.FloatField(default=0)
    assists = models.FloatField(default=0)
    steals = models.FloatField(default=0)
    blocks = models.FloatField(default=0)
    turnovers = models.FloatField(default=0)

    fg_pct = models.FloatField(null=True, blank=True)
    fg3_pct = models.FloatField(null=True, blank=True)
    ft_pct = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("player", "season")

    def __str__(self) -> str:
        return f"{self.player} – {self.season}"


class PlayerGameStat(models.Model):
    """
    WNBA Mystics player game log – used for the trend chart on the roster page.
    """
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="game_stats",
    )
    game_date = models.DateField()
    opponent = models.CharField(max_length=64)
    points = models.FloatField()
    rebounds = models.FloatField()
    assists = models.FloatField()
    minutes = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("player", "game_date")
        ordering = ["game_date"]

    def __str__(self) -> str:
        return f"{self.player} – {self.game_date}"

