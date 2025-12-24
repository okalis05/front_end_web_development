from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PipelineRun
from .services.events import emit_pipeline_update, emit_run_update


@receiver(post_save, sender=PipelineRun)
def broadcast_run_update(sender, instance: PipelineRun, **kwargs):
    payload = {
        "event": "run_status",
        "run_id": instance.id,
        "pipeline": instance.pipeline.slug,
        "status": instance.status,
        "prefect_state": instance.prefect_state,
        "duration_seconds": instance.duration_seconds,
    }
    emit_pipeline_update(instance.pipeline.slug, payload)
    emit_run_update(instance.id, payload)
