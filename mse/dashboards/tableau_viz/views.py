
from __future__ import annotations

from django.conf import settings
from django.shortcuts import render

from .services.tableau import get_embed


CMS_DATASET_URL = "https://data.cms.gov/provider-data/dataset/9n3s-kdb3"

# Create your views here.
def _hosts_display() -> str:
    raw = getattr(settings, "TABLEAU_EMBED_ALLOWED_HOSTS", "")
    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    return ", ".join(hosts) if hosts else "none"


NAV = [
    {"label": "Executive", "href": "dashboards:tableau_viz:executive_overview", "key": "executive_overview"},
    {"label": "Readmissions", "href": "dashboards:tableau_viz:readmissions", "key": "readmissions"},
    {"label": "Cost Impact", "href": "dashboards:tableau_viz:cost_impact", "key": "cost_impact"},
    {"label": "Hospital", "href": "dashboards:tableau_viz:hospital_profile", "key": "hospital_profile"},
]

TITLES = {
    "executive_overview": ("Executive Overview", "Board KPIs · at-risk facilities · concentration"),
    "readmissions": ("Readmissions & Outcomes", "Expected vs predicted · drivers · volume context"),
    "cost_impact": ("Cost & Utilization Impact", "High-volume risk quadrant · CFO view"),
    "hospital_profile": ("Hospital Profile", "Facility scorecard · drill-through"),
}


def _base_context(*, page_title: str = "Executive Dashboards", active: str = "landing") -> dict:
    return {
        "page_title": page_title,
        "active": active,
        "cms_dataset_url": CMS_DATASET_URL,
        "tableau_hosts": _hosts_display(),
        "nav": [
            {"label": "Executive", "href": "tableau_viz:executive_overview", "key": "executive_overview"},
            {"label": "CMO", "href": "tableau_viz:readmissions", "key": "readmissions"},
            {"label": "CFO", "href": "tableau_viz:cost_impact", "key": "cost_impact"},
            {"label": "Hospital", "href": "tableau_viz:hospital_profile", "key": "hospital_profile"},
            {"label": "Data", "href": "tableau_viz:data_sources", "key": "data_sources"},
        ],
    }


def landing(request):
    ctx = {
        "page_title": "Dashboards",
        "active": "landing",
        "nav": NAV,
        "cms_dataset_url": CMS_DATASET_URL,
        "tableau_hosts": _hosts_display(),
    }
    return render(request, "tableau_viz/landing.html", ctx)


def viz(request, view_key: str, facility_id: str | None = None):
    title, subtitle = TITLES.get(view_key, ("Dashboards", ""))
    embed = get_embed(view_key=view_key, facility_id=facility_id)

    ctx = {
        "page_title": title,
        "active": view_key,
        "nav": NAV,
        "cms_dataset_url": CMS_DATASET_URL,
        "tableau_hosts": _hosts_display(),
        "view_key": view_key,
        "title": title,
        "subtitle": subtitle,
        "embed": embed,
        "facility_id": facility_id,
    }
    return render(request, "tableau_viz/view.html", ctx)


def data_sources(request):
    ctx = _base_context(page_title="Data Sources & Governance", active="data_sources")
    return render(request, "tableau_viz/data_sources.html", ctx)
