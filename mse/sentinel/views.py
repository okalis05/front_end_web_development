from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.db.models import Max
from django.utils.timezone import localtime

from sentinel.industry.registry import list_industries, get_industry_config
from sentinel.models import Metric, Event



# Create your views here.
ALLOWED = {"sports", "mortgage", "retail", "healthcare"}

@never_cache
def portal(request):
    # Landing page: ONLY wave animation + hover option. No extra UI.
    return render(request, "sentinel/portal.html", {"industries": list_industries()})

@never_cache
def industry_home(request, industry_key: str):
    if industry_key not in ALLOWED:
        raise Http404("Unknown industry")

    cfg = get_industry_config(industry_key)
    return render(request, "sentinel/industry.html", {"cfg": cfg})

@never_cache
def api_industries(request):
    return JsonResponse({"industries": list_industries()})

@never_cache
def api_metrics(request, industry_key: str):
    if industry_key not in ALLOWED:
        return JsonResponse({"error": "Unknown industry"}, status=404)

    cfg = get_industry_config(industry_key)
    metrics_out = []

    # Latest metric per KPI (fast enough for MVP)
    for kpi in cfg["kpis"]:
        row = (
            Metric.objects
            .filter(industry_key=industry_key, kpi_key=kpi["key"])
            .order_by("-ts")
            .values("value", "ts")
            .first()
        )
        val = float(row["value"]) if row else float(kpi["baseline"])
        ts = localtime(row["ts"]).isoformat() if row else None

        metrics_out.append({
            "kpi_key": kpi["key"],
            "label": kpi["label"],
            "unit": kpi["unit"],
            "value": val,
            "ts": ts
        })

    return JsonResponse({"industry_key": industry_key, "metrics": metrics_out})

@never_cache
def api_events(request, industry_key: str):
    if industry_key not in ALLOWED:
        return JsonResponse({"error": "Unknown industry"}, status=404)

    limit = request.GET.get("limit", "50")
    try:
        limit_i = max(1, min(200, int(limit)))
    except ValueError:
        limit_i = 50

    rows = (
        Event.objects
        .filter(industry_key=industry_key)
        .order_by("-ts")[:limit_i]
        .values("id", "event_type", "severity", "title", "body", "kpi_key", "value", "ts")
    )

    events = []
    for e in rows:
        events.append({
            "id": e["id"],
            "event_type": e["event_type"],
            "severity": e["severity"],
            "title": e["title"],
            "body": e["body"],
            "kpi_key": e["kpi_key"],
            "value": float(e["value"]),
            "ts": localtime(e["ts"]).isoformat()
        })

    return JsonResponse({"industry_key": industry_key, "events": events})
