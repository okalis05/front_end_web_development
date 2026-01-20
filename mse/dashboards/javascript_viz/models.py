from __future__ import annotations
from django.db import models


# Create your models here.
class Loan(models.Model):
    """
    Simple loan record for portfolio analytics.
    """
    GRADE_CHOICES = [(g, g) for g in ["A", "B", "C", "D", "E", "F", "G"]]
    STATUS_CHOICES = [(s, s) for s in ["current", "late", "default", "paid"]]

    loan_id = models.CharField(max_length=32, unique=True)
    origination_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    apr = models.DecimalField(max_digits=6, decimal_places=2)  # percent
    term_months = models.PositiveIntegerField(default=36)

    grade = models.CharField(max_length=1, choices=GRADE_CHOICES)
    state = models.CharField(max_length=2)
    fico_band = models.CharField(max_length=16, default="680-719")
    purpose = models.CharField(max_length=48, default="debt_consolidation")

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="current")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["origination_date"]),
            models.Index(fields=["grade"]),
            models.Index(fields=["state"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.loan_id} ({self.grade})"


class Payment(models.Model):
    """
    Monthly payments / performance snapshots.
    """
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    as_of = models.DateField()

    principal_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_late = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ("loan", "as_of")
        indexes = [
            models.Index(fields=["as_of"]),
            models.Index(fields=["is_late"]),
            models.Index(fields=["is_default"]),
        ]

    def __str__(self) -> str:
        return f"{self.loan.loan_id} @ {self.as_of}"


class MetricSnapshot(models.Model):
    """
    Pre-aggregated metrics for fast dashboard loads.
    """
    as_of = models.DateField(db_index=True)

    portfolio_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    revenue_interest = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    chargeoffs = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    default_rate = models.DecimalField(max_digits=7, decimal_places=4, default=0)  # 0..1
    late_rate = models.DecimalField(max_digits=7, decimal_places=4, default=0)     # 0..1
    expected_loss = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("as_of",)

    def __str__(self) -> str:
        return f"Metrics {self.as_of}"


class AlertEvent(models.Model):
    """
    Real-time events streamed to the UI via WebSockets.
    """
    EVENT_TYPES = [(t, t) for t in ["risk_spike", "fraud_signal", "portfolio_alert", "system"]]

    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES)
    severity = models.PositiveSmallIntegerField(default=2)  # 1..5
    title = models.CharField(max_length=120)
    detail = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["ts", "event_type"])]

    def __str__(self) -> str:
        return f"[{self.event_type}] {self.title}"
