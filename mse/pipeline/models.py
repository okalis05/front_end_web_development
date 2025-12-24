from django.db import models
from django.utils import timezone


class Pipeline(models.Model):
    """
    Business-level pipeline (e.g. 'Mystics Raw → Analytics Models').

    Orchestration options:
    - Prefect deployment name (recommended): e.g. 'mse-pipeline/dbt-build'
    - Local dbt execution (fallback) if Prefect isn't configured
    """
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    description = models.TextField(blank=True)

    # SLA / health config
    sla_minutes = models.IntegerField(default=60)
    health_target_success_rate = models.FloatField(default=0.95)
    health_window_runs = models.IntegerField(default=20)

    # RBAC
    allowed_groups = models.ManyToManyField("auth.Group", blank=True)

    # Prefect (deployment name in Prefect v2+)
    prefect_deployment_name = models.CharField(max_length=200, blank=True)

    owner = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    # UI accents
    accent = models.CharField(max_length=40, default="electric")  # electric|sunrise|hyper|mint

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = [
            ("can_trigger_pipeline", "Can trigger pipeline runs"),
            ("can_view_pipeline", "Can view pipeline dashboards"),
        ]

    def __str__(self) -> str:
        return self.name


class PipelineRun(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("UNKNOWN", "Unknown"),
    ]

    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="runs")

    # Prefect identifiers
    prefect_flow_run_id = models.CharField(max_length=64, blank=True, db_index=True)
    prefect_state = models.CharField(max_length=40, default="UNKNOWN", db_index=True)

    triggered_by = models.CharField(max_length=120, blank=True)
    parameters = models.JSONField(default=dict, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="PENDING", db_index=True)

    # Executive rollups
    duration_seconds = models.IntegerField(null=True, blank=True)
    rows_extracted = models.IntegerField(null=True, blank=True)
    rows_loaded = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.pipeline.slug} run {self.id} [{self.status}]"


class PipelineArtifact(models.Model):
    run = models.ForeignKey(PipelineRun, on_delete=models.CASCADE, related_name="artifacts")
    key = models.CharField(max_length=120)
    value = models.TextField(blank=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("run", "key")]

    def __str__(self) -> str:
        return f"{self.run_id}:{self.key}"
