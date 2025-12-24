from __future__ import annotations
from django.conf import settings
from django.db import models
from django.utils import timezone


class AutoBuyerSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auto_sessions",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    state = models.JSONField(default=dict, blank=True)
    credit_snapshot = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"AutoBuyerSession({self.id})"


class AutoBuyerMessage(models.Model):
    session = models.ForeignKey(
        AutoBuyerSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    created_at = models.DateTimeField(default=timezone.now)

    role = models.CharField(
        max_length=16,
        choices=[("user", "user"), ("assistant", "assistant")],
    )
    agent = models.CharField(max_length=64, blank=True, default="")
    content = models.TextField()
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:40]}"


class BuyerPlan(models.Model):
    """
    Executive buyer plan associated with an AI Auto session.
    One user may have multiple plans across sessions.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="buyer_plans",
    )
    session = models.ForeignKey(
        AutoBuyerSession,
        on_delete=models.CASCADE,
        related_name="buyer_plans",
    )
    created_at = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=120, default="Buyer Plan")
    checklist = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"BuyerPlan({self.id})"


class BuyerPlanVehicle(models.Model):
    """
    Vehicle saved into a buyer plan.
    This is the model expected by ai_auto views.
    """
    plan = models.ForeignKey(
        BuyerPlan,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )
    created_at = models.DateTimeField(default=timezone.now)

    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.PositiveIntegerField(null=True, blank=True)
    trim = models.CharField(max_length=64, blank=True, default="")
    price = models.PositiveIntegerField(null=True, blank=True)

    badge = models.CharField(
        max_length=32,
        blank=True,
        default="",  # Conservative / Balanced / Stretch
    )

    inventory_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
    )

    meta = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.year} {self.make} {self.model}"
