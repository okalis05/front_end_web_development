from __future__ import annotations

import json
from django.utils.timezone import localtime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def _group(industry_key: str) -> str:
    # group names must be ascii + safe
    return f"sentinel.{industry_key}"


def _send(industry_key: str, event_name: str, payload: dict) -> None:
    """
    Broadcast payload to all SSE subscribers for an industry via Channels group.
    This is the "emit_*" layer you asked for.
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    msg = {
        "type": "sentinel.message",
        "event": event_name,
        "payload": payload,
    }
    async_to_sync(channel_layer.group_send)(_group(industry_key), msg)


def emit_metric_tick(*, industry_key: str, kpi_key: str, label: str, unit: str, value: float, ts) -> None:
    payload = {
        "kpi_key": kpi_key,
        "label": label,
        "unit": unit,
        "value": float(value),
        "ts": localtime(ts).isoformat(),
    }
    _send(industry_key, "metric", payload)


def emit_event_created(
    *,
    industry_key: str,
    event_id: int,
    event_type: str,
    severity: int,
    title: str,
    body: str,
    kpi_key: str,
    value: float,
    ts,
) -> None:
    payload = {
        "id": int(event_id),
        "event_type": event_type,
        "severity": int(severity),
        "title": title,
        "body": body,
        "kpi_key": kpi_key or "",
        "value": float(value),
        "ts": localtime(ts).isoformat(),
    }
    _send(industry_key, "event", payload)
