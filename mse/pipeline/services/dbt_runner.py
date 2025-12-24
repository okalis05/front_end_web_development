import os
import subprocess
from dataclasses import dataclass
from pipeline.services.dbt_runner import *  



@dataclass
class DBTResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int
    cmd: list[str]


def run_dbt_command(args: list[str]) -> DBTResult:
    project_dir = os.getenv("PIPELINE_DBT_PROJECT_DIR")
    profiles_dir = os.getenv("PIPELINE_DBT_PROFILES_DIR") or project_dir

    if not project_dir:
        return DBTResult(False, "", "PIPELINE_DBT_PROJECT_DIR not set", 2, ["dbt"] + args)

    cmd = ["dbt"] + args + ["--project-dir", project_dir]
    if profiles_dir:
        cmd += ["--profiles-dir", profiles_dir]

    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return DBTResult(p.returncode == 0, p.stdout or "", p.stderr or "", p.returncode, cmd)
    except FileNotFoundError:
        return DBTResult(False, "", "dbt executable not found. Install dbt and ensure it's on PATH.", 127, cmd)
