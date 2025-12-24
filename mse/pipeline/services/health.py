from django.utils import timezone


def compute_health(pipeline):
    runs = list(pipeline.runs.order_by("-created_at")[:pipeline.health_window_runs])

    if not runs:
        return {"score": 0, "grade": "N/A", "message": "No runs yet", "success_rate": 0.0, "success_rate_pct": 0.0}

    total = len(runs)
    failures = sum(1 for r in runs if r.status in {"FAILED", "CANCELLED"})
    success = sum(1 for r in runs if r.status == "COMPLETED")
    success_rate = success / total if total else 0.0

    durations = [r.duration_seconds for r in runs if r.duration_seconds is not None]
    mean_runtime = int(sum(durations) / len(durations)) if durations else None

    last_success = next((r for r in runs if r.status == "COMPLETED"), None)
    last_success_age_min = None
    if last_success:
        last_success_age_min = int((timezone.now() - last_success.created_at).total_seconds() / 60)

    score = 100
    score -= int((1 - success_rate) * 120)
    if mean_runtime is not None and mean_runtime > pipeline.sla_minutes * 60:
        score -= 20
    if last_success_age_min is not None and last_success_age_min > pipeline.sla_minutes * 6:
        score -= 20

    score = max(0, min(100, score))
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"

    if grade in {"A", "B"}:
        msg = "Healthy"
    elif grade == "C":
        msg = "Watchlist"
    else:
        msg = "At risk"

    return {
        "score": score,
        "grade": grade,
        "message": msg,
        "success_rate": round(success_rate, 3),          # 0..1
        "success_rate_pct": round(success_rate * 100, 1),# 0..100
        "failures": failures,
        "mean_runtime_seconds": mean_runtime,
        "last_success_age_minutes": last_success_age_min,
    }
