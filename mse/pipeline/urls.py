from django.urls import path
from . import views

app_name = "pipeline"

urlpatterns = [
    # Command Center
    path("", views.command_center, name="command_center"),

    # Pipeline detail (two names, same path)
    path("pipelines/<slug:slug>/", views.pipeline_detail, name="detail"),
    path("pipelines/<slug:slug>/", views.pipeline_detail, name="pipeline_detail"),

    # Trigger
    path("pipelines/<slug:slug>/trigger/", views.trigger_pipeline, name="trigger_pipeline"),

    # Run detail
    path("runs/<int:run_id>/", views.run_detail, name="run_detail"),

    # APIs (match JS)
    path("api/pipelines/<slug:slug>/latest-runs/", views.api_latest_runs, name="api_latest_runs"),
    path("api/runs/<int:run_id>/refresh/", views.api_refresh_run, name="api_refresh_run"),
]
