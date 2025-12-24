from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def emit_pipeline_update(pipeline_slug: str, payload: dict):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f"pipeline_{pipeline_slug}",
        {
            "type": "pipeline_update",
            "payload": payload,
        },
    )


def emit_run_update(run_id: int, payload: dict):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f"run_{run_id}",
        {
            "type": "run_update",
            "payload": payload,
        },
    )
