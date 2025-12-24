from django.contrib import admin
from .models import Pipeline, PipelineRun, PipelineArtifact


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "prefect_deployment_name", "accent", "created_at")
    list_filter = ("is_active", "accent")
    search_fields = ("name", "slug", "prefect_deployment_name")
    filter_horizontal = ("allowed_groups",)


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ("pipeline", "status", "prefect_state", "prefect_flow_run_id", "created_at", "started_at", "finished_at")
    list_filter = ("status", "prefect_state", "pipeline")
    search_fields = ("prefect_flow_run_id", "pipeline__slug")
    readonly_fields = ("created_at", "started_at", "finished_at", "duration_seconds")


@admin.register(PipelineArtifact)
class PipelineArtifactAdmin(admin.ModelAdmin):
    list_display = ("run", "key", "url", "created_at")
    search_fields = ("key", "run__prefect_flow_run_id")
    readonly_fields = ("created_at",)
