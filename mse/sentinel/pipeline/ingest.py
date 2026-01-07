import random
from django.utils import timezone
from sentinel.industry.registry import get_industry_config
from sentinel.models import Metric, Event
from sentinel.pipeline.anomalies import rolling_zscore

# NEW: realtime emits (Channels group broadcast)
from sentinel.services.events import emit_metric_tick, emit_event_created


def _jitter(base: float) -> float:
    r = random.random()
    if r < 0.90:
        scale = random.uniform(-0.02, 0.02)
    elif r < 0.98:
        scale = random.uniform(-0.06, 0.06)
    else:
        scale = random.uniform(-0.16, 0.16)
    return max(0.0, base + base * scale)


def ingest_tick(industry_key: str) -> None:
    cfg = get_industry_config(industry_key)

    for kpi in cfg["kpis"]:
        kpi_key = kpi["key"]
        baseline = float(kpi["baseline"])
        new_val = _jitter(baseline)

        recent = (
            Metric.objects
            .filter(industry_key=industry_key, kpi_key=kpi_key)
            .order_by("-ts")
            .values_list("value", flat=True)[:30]
        )
        hist = list(reversed(list(recent)))  # chronological
        res = rolling_zscore(hist[-20:], new_val, min_n=10)

        m = Metric.objects.create(
            industry_key=industry_key,
            kpi_key=kpi_key,
            value=float(new_val),
            ts=timezone.now()
        )

        # NEW: push metric tick live (SSE)
        emit_metric_tick(
            industry_key=industry_key,
            kpi_key=kpi_key,
            label=kpi["label"],
            unit=kpi["unit"],
            value=float(new_val),
            ts=m.ts,
        )

        if res.is_anomaly:
            direction = "spiked" if res.z > 0 else "dropped"
            sev = 5 if abs(res.z) >= 3.0 else 4

            action0 = cfg["recommended_actions"][0]
            title = f"{kpi['label']} {direction} (z={res.z:+.2f})"
            body = (
                f"{cfg['label']} anomaly detected for {kpi['label']}. "
                f"Observed {new_val:.2f}{kpi['unit']} vs mean {res.mean:.2f} (σ={res.std:.2f}). "
                f"Recommended: {action0['title']} — {action0['detail']}"
            )

            ev = Event.objects.create(
                industry_key=cfg["key"],
                event_type="anomaly",
                severity=sev,
                title=title,
                body=body,
                kpi_key=kpi_key,
                value=float(new_val),
                ts=timezone.now()
            )

            # NEW: push event live (SSE)
            emit_event_created(
                industry_key=cfg["key"],
                event_id=ev.id,
                event_type=ev.event_type,
                severity=ev.severity,
                title=ev.title,
                body=ev.body,
                kpi_key=ev.kpi_key,
                value=float(ev.value),
                ts=ev.ts,
            )
