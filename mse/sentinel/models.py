from django.db import models

# Create your models here.
class Metric(models.Model):
    industry_key = models.CharField(max_length=32, db_index=True)
    kpi_key = models.CharField(max_length=64, db_index=True)
    value = models.FloatField()
    ts = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["industry_key", "kpi_key", "-ts"]),
        ]

    def __str__(self):
        return f"{self.industry_key}:{self.kpi_key}={self.value:.2f}"

class Event(models.Model):
    industry_key = models.CharField(max_length=32, db_index=True)
    event_type = models.CharField(max_length=64, db_index=True)  # anomaly, info, action
    severity = models.PositiveSmallIntegerField(default=1)        # 1..5
    title = models.CharField(max_length=160)
    body = models.TextField()
    kpi_key = models.CharField(max_length=64, blank=True, default="")
    value = models.FloatField(blank=True, default=0.0)
    ts = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["industry_key", "-ts"]),
            models.Index(fields=["event_type", "-ts"]),
        ]

    def __str__(self):
        return f"[{self.industry_key}] {self.event_type} sev{self.severity}: {self.title}"
