from __future__ import annotations

import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST
from banking.ai_auto.models import AutoBuyerSession
from .policy import recommend_terms
from .services import score, train_credit_model
from .models import CreditApplication
from django.conf import settings

def _ai_enabled(request: HttpRequest) -> bool:
    return bool(getattr(settings, "BANKING_AI_ENABLED", False))


@login_required
def ai_credit_home(request):
    if not getattr(settings, "BANKING_AI_ENABLED", False):
        return render(request, "banking/disabled.html", status=404)

    # Latest AI Auto session (if exists)
    auto_session = (
        AutoBuyerSession.objects
        .filter(user=request.user, is_active=True)
        .order_by("-updated_at")
        .first()
    )

    prefill = {}
    if auto_session and auto_session.state:
        state = auto_session.state
        prefill = {
            "loan_amnt": state.get("price_cap_est"),
            "term": f"{state.get('term_months', 60)} months" if state.get("term_months") else None,
            "annual_inc": state.get("annual_income"),
            "dti": state.get("dti"),
        }

    recent = CreditApplication.objects.filter(user=request.user).order_by("-created_at")[:10]

    return render(
        request,
        "banking/ai_credit/home.html",
        {
            "recent": recent,
            "prefill": prefill,   # 🔑 THIS
        },
    )



@require_POST
@login_required
def score_credit(request: HttpRequest):
    if not _ai_enabled(request):
        return JsonResponse({"ok": False, "error": "AI disabled"}, status=404)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    scored = score(payload)
    prob = float(scored["prob_default"])
    terms = recommend_terms(prob, payload.get("loan_amnt", 0))

    CreditApplication.objects.create(
        user=request.user,
        input_data=payload,
        prob_default=prob,
        risk_tier=terms["risk_tier"],
        decision=terms["decision"],
        recommended_terms=terms,
        model_version=scored["model_version"],
    )

    return JsonResponse({
        "ok": True,
        "prob_default": round(prob, 3),
        "model_version": scored["model_version"],
        **terms,
    })


def _is_staff(user) -> bool:
    return user.is_staff or user.is_superuser


@require_POST
@user_passes_test(_is_staff)
def retrain_credit_model(request: HttpRequest):
    """
    Governance: retrain model (staff-only)
    Body: {"csv_path": "...", "version": "v2"}
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    csv_path = payload.get("csv_path")
    version = payload.get("version", "v2")
    if not csv_path:
        return JsonResponse({"ok": False, "error": "csv_path required"}, status=400)

    artifact = train_credit_model(csv_path=csv_path, version=version)
    return JsonResponse({"ok": True, "version": artifact.version, "metrics": artifact.metrics})
