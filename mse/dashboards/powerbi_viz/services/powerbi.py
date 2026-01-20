from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from django.conf import settings


@dataclass(frozen=True)
class PowerBIReport:
    key: str
    title: str
    subtitle: str
    embed_url: str
    section_id: str


def _registry() -> Dict[str, Dict[str, Any]]:
    """
    Read the registry from Django settings.
    """
    raw = getattr(settings, "POWERBI_VIZ_REPORTS", None)
    if not isinstance(raw, dict):
        return {}
    return raw


def get_report(key: str) -> PowerBIReport:
    reg = _registry()
    if key not in reg:
        raise KeyError(f"POWERBI_VIZ_REPORTS missing key: {key}")

    item = reg[key]
    for req in ("title", "subtitle", "embed_url", "section_id"):
        if req not in item or not str(item[req]).strip():
            raise ValueError(f"POWERBI_VIZ_REPORTS[{key!r}] missing/empty field: {req}")

    return PowerBIReport(
        key=key,
        title=str(item["title"]),
        subtitle=str(item["subtitle"]),
        embed_url=str(item["embed_url"]),
        section_id=str(item["section_id"]),
    )


def list_reports() -> list[PowerBIReport]:
    reg = _registry()
    reports: list[PowerBIReport] = []
    for key in reg.keys():
        try:
            reports.append(get_report(key))
        except Exception:
            # fail-safe: skip malformed entries
            continue
    return reports


def build_embed_url(base_url: str, *, page: str | None = None) -> str:
    if not page:
        return base_url
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}pageName={page}"

def with_page(report: PowerBIReport, page: str | None) -> PowerBIReport:
    return PowerBIReport(
        key=report.key,
        title=report.title,
        subtitle=report.subtitle,
        section_id=report.section_id,
        embed_url=build_embed_url(report.embed_url, page=page),
    )
