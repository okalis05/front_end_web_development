from __future__ import annotations

import json
from ast import literal_eval
from dataclasses import asdict, is_dataclass
from typing import Any, Dict

from django.http import Http404
from django.shortcuts import render

from .data import get_case_by_slug, get_case_studies


def _normalize_payload(payload: Any) -> dict:
    """Return a Python dict always."""
    if payload is None:
        return {}

    if isinstance(payload, dict):
        return payload

    if isinstance(payload, list):
        return {"rows": payload}

    if isinstance(payload, str):
        s = payload.strip()

        # JSON string?
        try:
            if s.startswith("{") or s.startswith("["):
                parsed = json.loads(s)
                if isinstance(parsed, dict):
                    return parsed
                if isinstance(parsed, list):
                    return {"rows": parsed}
        except Exception:
            pass

        # Python repr string?
        try:
            parsed = literal_eval(s)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                return {"rows": parsed}
        except Exception:
            pass

    return {}


def _to_view_case(case: Any) -> Dict[str, Any]:
    """Convert case to mutable dict + prepare payload_json for JS."""
    if case is None:
        return {}

    if isinstance(case, dict):
        view_case: Dict[str, Any] = dict(case)
    elif is_dataclass(case):
        view_case = asdict(case)
    else:
        view_case = {
            "title": getattr(case, "title", ""),
            "hero_tagline": getattr(case, "hero_tagline", ""),
            "mission": getattr(case, "mission", ""),
            "dataset_note": getattr(case, "dataset_note", ""),
            "final_answer_title": getattr(case, "final_answer_title", ""),
            "final_answer": getattr(case, "final_answer", ""),
            "recommendations": getattr(case, "recommendations", []) or [],
            "next_steps": getattr(case, "next_steps", []) or [],
            "blocks": getattr(case, "blocks", []) or [],
            "slug": getattr(case, "slug", ""),
        }

    blocks = view_case.get("blocks") or []
    norm_blocks = []

    for b in blocks:
        if isinstance(b, dict):
            bd = dict(b)
        elif is_dataclass(b):
            bd = asdict(b)
        else:
            bd = {
                "title": getattr(b, "title", ""),
                "sub_question": getattr(b, "sub_question", ""),
                "chart_type": getattr(b, "chart_type", ""),
                "kpis": getattr(b, "kpis", []) or [],
                "insights": getattr(b, "insights", []) or [],
                "mission_link": getattr(b, "mission_link", ""),
                "payload": getattr(b, "payload", None),
            }

        # ✅ normalize to dict
        payload_dict = _normalize_payload(bd.get("payload"))
        bd["payload"] = payload_dict

        # ✅ create real JSON string for safe injection into <script type="application/json">
        bd["payload_json"] = json.dumps(payload_dict, ensure_ascii=False)

        norm_blocks.append(bd)

    view_case["blocks"] = norm_blocks
    return view_case


def index(request):
    cases = get_case_studies()
    return render(
        request,
        "javascript_viz/index.html",
        {
            "page_title": "JavaScript Viz",
            "cases": cases,
        },
    )


def dashboard(request, slug: str):
    case = get_case_by_slug(slug)
    if not case:
        raise Http404("Dashboard not found")

    view_case = _to_view_case(case)

    return render(
        request,
        "javascript_viz/dashboard.html",
        {
            "page_title": view_case.get("title", "JavaScript Viz"),
            "case": view_case,
        },
    )
