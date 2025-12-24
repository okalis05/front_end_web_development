from prefect import flow, task
from pipeline.services.dbt_runner import run_dbt_command

@task(retries=1)
def dbt_build(select: str | None = None):
    args = ["build"]
    if select:
        args += ["--select", select]
    res = run_dbt_command(args)
    if not res.ok:
        raise RuntimeError(f"dbt build failed:\n{res.stderr}")
    return {"stdout": res.stdout[-20000:]}

@task
def dbt_docs():
    res = run_dbt_command(["docs", "generate"])
    if not res.ok:
        raise RuntimeError(f"dbt docs generate failed:\n{res.stderr}")
    return {"stdout": res.stdout[-20000:]}

@flow(name="mse_pipeline_dbt_build")
def mse_pipeline_dbt_build(select: str | None = None, generate_docs: bool = True):
    """
    Transform raw → analytics-ready models using dbt build. :contentReference[oaicite:8]{index=8}
    """
    out = dbt_build(select)
    if generate_docs:
        dbt_docs()
    return out
