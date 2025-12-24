from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CreditModelArtifact(models.Model):
    version = models.CharField(max_length=32)
    created_at = models.DateTimeField(default=timezone.now)
    artifact_path = models.CharField(max_length=512)
    metrics = models.JSONField(default=dict)
    feature_schema = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"CreditModelArtifact({self.version})"


class CreditApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    input_data = models.JSONField(default=dict)

    prob_default = models.FloatField()
    risk_tier = models.CharField(max_length=16)  # LOW/MEDIUM/HIGH
    decision = models.CharField(max_length=16)   # APPROVE/REVIEW/DECLINE

    recommended_terms = models.JSONField(default=dict)  # includes explainability
    model_version = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f"CreditApplication({self.id}, {self.risk_tier})"
