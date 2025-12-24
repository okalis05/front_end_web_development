from django.apps import AppConfig


class PipelineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pipeline"
    verbose_name = "Data Pipeline (Prefect + dbt)"

    def ready(self):
        # Ensure signals register
        import pipeline.signals  # noqa
