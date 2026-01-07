from __future__ import annotations

from django.http import Http404
from django.shortcuts import render
from django.conf import settings

from .services.tableau import get_view


# Create your views here.
NAV = [
    {"label": "Executive Overview", "href": "dashboard:executive_overview"},
    {"label": "Readmissions", "href": "dashboard:readmissions"},
    {"label": "Cost Impact", "href": "dashboard:cost_impact"},
    {"label": "Data", "href": "dashboard:data_sources"},
]


def _base_context(**kwargs):
    return {
        "nav": NAV,
        "cms_dataset_url": "https://data.cms.gov/provider-data/dataset/9n3s-kdb3",
        "tableau_hosts": getattr(settings, "TABLEAU_EMBED_ALLOWED_HOSTS", ""),
        **kwargs,
    }


def landing(request):
    return render(request, "dashboard/landing.html", _base_context())


def executive_overview(request):
    embed = get_view("executive_overview")
    return render(
        request,
        "dashboard/executive_overview.html",
        _base_context(
            page_title="Executive Overview",
            embed=embed,
            view_key="executive_overview",
        ),
    )


def readmissions(request):
    embed = get_view("readmissions")
    return render(
        request,
        "dashboard/readmissions.html",
        _base_context(
            page_title="Readmissions & Clinical Outcomes",
            embed=embed,
            view_key="readmissions",
        ),
    )


def cost_impact(request):
    embed = get_view("cost_impact")
    return render(
        request,
        "dashboard/cost_impact.html",
        _base_context(
            page_title="Cost & Utilization Impact",
            embed=embed,
            view_key="cost_impact",
        ),
    )


def hospital_profile(request, facility_id: str):
    embed = get_view("hospital_profile")
    # Optional: if your Tableau URL supports parameters, you can pass facility_id to the iframe
    # by appending something like "&FacilityID=<id>" within the template JS (kept secure).
    return render(
        request,
        "dashboard/hospital_profile.html",
        _base_context(
            page_title=f"Hospital Profile: {facility_id}",
            embed=embed,
            facility_id=facility_id,
            view_key="hospital_profile",
        ),
    )


def data_sources(request):
    return render(
        request,
        "dashboard/data_sources.html",
        _base_context(page_title="Data Sources & Governance"),
    )
