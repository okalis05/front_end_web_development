from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PrefectAPI:
    """
    Minimal Prefect HTTP client with retries + timeouts.

    Env:
      PREFECT_API_URL (e.g. http://127.0.0.1:4200/api)
      PREFECT_API_TOKEN (optional)
      PREFECT_HTTP_TIMEOUT (seconds, default 10)

    Notes:
      - Prefect v2 typically uses deployments to create runs.
      - We'll try deployment-name endpoint first when provided.
    """

    def __init__(self):
        self.base_url = (os.getenv("PREFECT_API_URL") or "http://127.0.0.1:4200/api").rstrip("/")
        self.token = os.getenv("PREFECT_API_TOKEN") or ""
        self.timeout = float(os.getenv("PREFECT_HTTP_TIMEOUT") or "10")

        self.session = requests.Session()
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.6,
            status_forcelist=(408, 429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT", "PATCH", "DELETE"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _url(self, path: str) -> str:
        path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{path}"

    def create_flow_run_for_deployment_name(self, deployment_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Prefect v2 endpoint:
        # POST /deployments/name/{deployment_name}/create_flow_run
        url = self._url(f"/deployments/name/{deployment_name}/create_flow_run")
        payload = {"parameters": parameters or {}}
        r = self.session.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Prefect create_flow_run (deployment name) failed ({r.status_code}): {r.text}")
        data = r.json()
        return data if isinstance(data, dict) else {"data": data}

    def create_flow_run(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Generic fallback
        url = self._url("/flow_runs/")
        payload = {"parameters": parameters or {}}
        r = self.session.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Prefect create_flow_run failed ({r.status_code}): {r.text}")
        data = r.json()
        return data if isinstance(data, dict) else {"data": data}

    def read_flow_run(self, flow_run_id: str) -> Dict[str, Any]:
        url = self._url(f"/flow_runs/{flow_run_id}")
        r = self.session.get(url, headers=self._headers(), timeout=self.timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"Prefect read_flow_run failed ({r.status_code}): {r.text}")
        data = r.json()
        return data if isinstance(data, dict) else {"data": data}
