import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required

from .models import Pipeline, PipelineRun, PipelineArtifact
from .services.health import compute_health
from .services.prefect_client import PrefectAPI
from .services.events import emit_run_update, emit_pipeline_update
from .services.dbt_runner import run_dbt_command
from .services.dbt_artifacts import ingest_dbt_artifacts


# -------------------------
# Prefect parsing (TESTED)
# -------------------------
def parse_prefect_state_name(payload: dict) -> str:
    """
    Accepts multiple Prefect shapes and returns normalized uppercase state.
    Tested in pipeline/tests.py
    """
    state = (
        (payload or {}).get("state_name")
        or (payload or {}).get("state", {}).get("name")
        or "UNKNOWN"
    )
    return str(state).upper()


def map_prefect_state_to_exec_status(state_name: str | None) -> str:
    """
    Map Prefect state → executive status.
    Tested in pipeline/tests.py
    """
    s = (state_name or "").upper()

    if s in {"COMPLETED", "SUCCESS"}:
        return "COMPLETED"
    if s in {"FAILED", "CRASHED"}:
        return "FAILED"
    if s in {"CANCELLED", "CANCELED"}:
        return "CANCELLED"
    if s in {"PENDING", "SCHEDULED"}:
        return "PENDING"
    # Default: treat everything else as running/active
    return "RUNNING"


# =========================
# COMMAND CENTER
# =========================
@permission_required("pipeline.can_view_pipeline", raise_exception=False)
def command_center(request):
    pipelines = Pipeline.objects.filter(is_active=True).order_by("name")
    recent_runs = PipelineRun.objects.select_related("pipeline").order_by("-created_at")[:15]

    return render(
        request,
        "pipeline/command_center.html",
        {
            "pipelines": pipelines,
            "recent_runs": recent_runs,
        },
    )


# =========================
# PIPELINE DETAIL
# =========================
@permission_required("pipeline.can_view_pipeline", raise_exception=False)
def pipeline_detail(request, slug):
    pipeline = get_object_or_404(Pipeline, slug=slug)
    runs = pipeline.runs.order_by("-created_at")[:30]
    health = compute_health(pipeline)

    return render(
        request,
        "pipeline/pipeline_detail.html",
        {
            "pipeline": pipeline,
            "runs": runs,
            "health": health,
        },
    )


# =========================
# TRIGGER PIPELINE
# =========================
@permission_required("pipeline.can_trigger_pipeline", raise_exception=True)
@require_POST
def trigger_pipeline(request, slug):
    pipeline = get_object_or_404(Pipeline, slug=slug)

    params = {
        "select": (request.POST.get("select") or "").strip() or None,
        "generate_docs": request.POST.get("generate_docs") == "true",
    }

    run = PipelineRun.objects.create(
        pipeline=pipeline,
        triggered_by=(request.user.username if request.user.is_authenticated else "anonymous"),
        parameters=params,
        status="PENDING",
        prefect_state="PENDING",
        started_at=None,
        finished_at=None,
    )

    # Decide orchestration path
    use_prefect = bool(pipeline.prefect_deployment_name) or bool((__import__("os").environ.get("PREFECT_API_URL") or "").strip())

    try:
        if use_prefect:
            api = PrefectAPI()
            if pipeline.prefect_deployment_name:
                resp = api.create_flow_run_for_deployment_name(pipeline.prefect_deployment_name, parameters=params)
            else:
                resp = api.create_flow_run(parameters=params)

            run.prefect_flow_run_id = str(resp.get("id") or "")
            run.prefect_state = "PENDING"
            run.status = "PENDING"
            run.save(update_fields=["prefect_flow_run_id", "prefect_state", "status"])

            messages.success(request, f"🚀 Pipeline triggered (Prefect run {run.prefect_flow_run_id[:8]}…)")

        else:
            # Local dbt fallback: run synchronously (safe for dev)
            run.started_at = timezone.now()
            run.prefect_state = "LOCAL"
            run.status = "RUNNING"
            run.save(update_fields=["started_at", "prefect_state", "status"])

            args = ["build"]
            if params["select"]:
                args += ["--select", params["select"]]

            res = run_dbt_command(args)

            # store last output chunk
            PipelineArtifact.objects.update_or_create(
                run=run, key="dbt_stdout_tail",
                defaults={"value": (res.stdout or "")[-20000:]}
            )
            PipelineArtifact.objects.update_or_create(
                run=run, key="dbt_stderr_tail",
                defaults={"value": (res.stderr or "")[-20000:]}
            )
            PipelineArtifact.objects.update_or_create(
                run=run, key="dbt_returncode",
                defaults={"value": str(res.returncode)}
            )

            # ingest artifacts from dbt/target if configured
            ingest_dbt_artifacts(run)

            run.finished_at = timezone.now()
            if run.started_at:
                run.duration_seconds = int((run.finished_at - run.started_at).total_seconds())

            if res.ok:
                run.status = "COMPLETED"
                messages.success(request, "✅ Local dbt build completed.")
            else:
                run.status = "FAILED"
                messages.error(request, "❌ Local dbt build failed. Check run detail for stderr tail.")

            run.save()

        # emit realtime update
        emit_pipeline_update(pipeline.slug, {
            "event": "triggered",
            "pipeline": pipeline.slug,
            "run_id": run.id,
        })
        emit_run_update(run.id, {
            "event": "triggered",
            "pipeline": pipeline.slug,
            "run_id": run.id,
        })

    except Exception as e:
        run.status = "FAILED"
        run.prefect_state = "FAILED"
        run.finished_at = timezone.now()
        if run.started_at:
            run.duration_seconds = int((run.finished_at - run.started_at).total_seconds())
        run.save()

        messages.error(request, f"Trigger failed: {e}")

    return redirect("pipeline:run_detail", run_id=run.id)


# =========================
# RUN DETAIL
# =========================
@permission_required("pipeline.can_view_pipeline", raise_exception=False)
def run_detail(request, run_id: int):
    run = get_object_or_404(PipelineRun.objects.select_related("pipeline"), id=run_id)
    artifacts = run.artifacts.order_by("key")

    # Pull dbt failures if present
    dbt_failures = []
    failures_art = artifacts.filter(key="dbt_test_failures").first()
    if failures_art and failures_art.value:
        try:
            dbt_failures = json.loads(failures_art.value) or []
        except Exception:
            dbt_failures = []

    return render(
        request,
        "pipeline/run_detail.html",
        {
            "run": run,
            "artifacts": artifacts,
            "dbt_failures": dbt_failures,
        },
    )


# =========================
# API: LATEST RUNS
# =========================
def api_latest_runs(request, slug):
    pipeline = get_object_or_404(Pipeline, slug=slug)
    runs = pipeline.runs.order_by("-created_at")[:10]

    data = [{
        "id": r.id,
        "status": r.status,
        "prefect_state": r.prefect_state,
        "created_at": r.created_at.isoformat(),
        "duration_seconds": r.duration_seconds,
    } for r in runs]

    return JsonResponse({"pipeline": pipeline.slug, "runs": data})


# =========================
# API: REFRESH RUN (LIVE)
# =========================
def api_refresh_run(request, run_id: int):
    run = get_object_or_404(PipelineRun, id=run_id)

    # Local runs don't have Prefect IDs
    if not run.prefect_flow_run_id:
        return JsonResponse(
            {"ok": True, "run": {
                "id": run.id,
                "status": run.status,
                "prefect_state": run.prefect_state,
                "duration_seconds": run.duration_seconds,
            }}
        )

    api = PrefectAPI()
    try:
        fr = api.read_flow_run(run.prefect_flow_run_id)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=502)

    state_name = parse_prefect_state_name(fr)
    mapped = map_prefect_state_to_exec_status(state_name)

    # update timestamps
    if mapped == "RUNNING" and not run.started_at:
        run.started_at = timezone.now()

    if mapped in {"COMPLETED", "FAILED", "CANCELLED"} and not run.finished_at:
        run.finished_at = timezone.now()
        if run.started_at:
            run.duration_seconds = int((run.finished_at - run.started_at).total_seconds())

    run.status = mapped
    run.prefect_state = state_name
    run.save()

    payload = {
        "event": "status",
        "pipeline": run.pipeline.slug,
        "run_id": run.id,
        "status": run.status,
        "prefect_state": run.prefect_state,
        "duration_seconds": run.duration_seconds,
    }

    emit_run_update(run.id, payload)
    emit_pipeline_update(run.pipeline.slug, payload)

    return JsonResponse({"ok": True, "run": payload})
