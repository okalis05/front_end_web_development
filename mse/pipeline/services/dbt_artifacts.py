import json
import os
from datetime import datetime
from pipeline.models import PipelineArtifact


def _read_json(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _parse_iso_dt(s: str | None):
    if not s:
        return None
    try:
        # Handle "Z"
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except Exception:
        return None


def ingest_dbt_artifacts(run, *, target_dir: str | None = None):
    project_dir = os.getenv("PIPELINE_DBT_PROJECT_DIR")
    if not target_dir:
        target_dir = os.path.join(project_dir, "target") if project_dir else None
    if not target_dir:
        return

    manifest = _read_json(os.path.join(target_dir, "manifest.json"))
    run_results = _read_json(os.path.join(target_dir, "run_results.json"))

    if manifest:
        nodes = manifest.get("nodes", {})
        PipelineArtifact.objects.update_or_create(
            run=run, key="dbt_manifest_node_count",
            defaults={"value": str(len(nodes))}
        )

    if run_results:
        results = run_results.get("results", []) or []
        status_counts: dict[str, int] = {}
        failures = []

        total_runtime = 0.0
        for r in results:
            status = (r.get("status") or "unknown").lower()
            status_counts[status] = status_counts.get(status, 0) + 1

            # timing (best-effort)
            for t in (r.get("timing") or []):
                s = _parse_iso_dt(t.get("started_at"))
                e = _parse_iso_dt(t.get("completed_at"))
                if s and e and e >= s:
                    total_runtime += (e - s).total_seconds()

            # capture failing tests (best-effort)
            unique_id = r.get("unique_id") or ""
            is_test = unique_id.startswith("test.") or "test" in unique_id
            if status in {"fail", "error"} and is_test:
                failures.append({
                    "key": unique_id,
                    "status": status.upper(),
                    "message": (r.get("message") or "")[:5000],
                    "failures": r.get("failures"),
                })

        PipelineArtifact.objects.update_or_create(
            run=run, key="dbt_run_results_count",
            defaults={"value": str(len(results))}
        )
        PipelineArtifact.objects.update_or_create(
            run=run, key="dbt_status_counts",
            defaults={"value": json.dumps(status_counts)}
        )
        PipelineArtifact.objects.update_or_create(
            run=run, key="dbt_total_runtime_seconds",
            defaults={"value": str(int(total_runtime))}
        )
        PipelineArtifact.objects.update_or_create(
            run=run, key="dbt_test_failures",
            defaults={"value": json.dumps(failures)}
        )
