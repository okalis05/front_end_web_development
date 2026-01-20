from __future__ import annotations

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .services.powerbi import (
    get_report,
    list_reports,
    build_embed_url,
)

# -------------------------
# Shared base context
# -------------------------
def _base_context(*, page_title: str, active_key: str) -> dict:
    return {
        "page_title": page_title,
        "active_key": active_key,
        "reports": list_reports(),
    }


# -------------------------
# Landing / long-scroll page
# -------------------------
def landing(request: HttpRequest) -> HttpResponse:
    ctx = _base_context(
        page_title="Power BI · Sports Executive Intelligence",
        active_key="landing",
    )

    keys = ["executive_overview", "player_impact", "health_risk", "revenue_fans"]
    sections = []
    for key in keys:
        try:
            sections.append(get_report(key))
        except Exception:
            # Fail-safe: allow page to render even if registry incomplete
            pass

    ctx["sections"] = sections
    return render(request, "powerbi_viz/landing.html", ctx)


# -------------------------
# Executive Overview
# -------------------------
def executive_overview(request: HttpRequest) -> HttpResponse:
    page = request.GET.get("page")

    base = get_report("executive_overview")
    report = base.__class__(
        key=base.key,
        title=base.title,
        subtitle=base.subtitle,
        section_id=base.section_id,
        embed_url=build_embed_url(base.embed_url, page=page),
    )

    ctx = _base_context(page_title=report.title, active_key=report.key)
    ctx["report"] = report
    return render(request, "powerbi_viz/landing.html", ctx)


# -------------------------
# Player Impact
# -------------------------
def player_impact(request: HttpRequest) -> HttpResponse:
    page = request.GET.get("page")

    base = get_report("player_impact")
    report = base.__class__(
        key=base.key,
        title=base.title,
        subtitle=base.subtitle,
        section_id=base.section_id,
        embed_url=build_embed_url(base.embed_url, page=page),
    )

    ctx = _base_context(page_title=report.title, active_key=report.key)
    ctx["report"] = report
    return render(request, "powerbi_viz/landing.html", ctx)


# -------------------------
# Health & Risk
# -------------------------
def health_risk(request: HttpRequest) -> HttpResponse:
    page = request.GET.get("page")

    base = get_report("health_risk")
    report = base.__class__(
        key=base.key,
        title=base.title,
        subtitle=base.subtitle,
        section_id=base.section_id,
        embed_url=build_embed_url(base.embed_url, page=page),
    )

    ctx = _base_context(page_title=report.title, active_key=report.key)
    ctx["report"] = report
    return render(request, "powerbi_viz/landing.html", ctx)


# -------------------------
# Revenue & Fans
# -------------------------
def revenue_fans(request: HttpRequest) -> HttpResponse:
    page = request.GET.get("page")

    base = get_report("revenue_fans")
    report = base.__class__(
        key=base.key,
        title=base.title,
        subtitle=base.subtitle,
        section_id=base.section_id,
        embed_url=build_embed_url(base.embed_url, page=page),
    )

    ctx = _base_context(page_title=report.title, active_key=report.key)
    ctx["report"] = report
    return render(request, "powerbi_viz/landing.html", ctx)
