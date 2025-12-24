from __future__ import annotations

import json
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .credit_bridge import fetch_credit_snapshot
from .inventory import nhtsa_makes, nhtsa_models, carquery_trims
from .models import AutoBuyerSession, AutoBuyerMessage, BuyerPlan, BuyerPlanVehicle
from .services import run_multi_agent


# -----------------------
# Feature gate + helpers
# -----------------------

def _ai_enabled() -> bool:
    return bool(getattr(settings, "BANKING_AI_ENABLED", False))


def _get_or_create_session(user) -> AutoBuyerSession:
    session = (
        AutoBuyerSession.objects
        .filter(user=user, is_active=True)
        .order_by("-updated_at")
        .first()
    )
    if not session:
        session = AutoBuyerSession.objects.create(user=user, state={}, is_active=True)
    return session


def _ensure_price_cap(state: Dict[str, Any]) -> None:
    """
    Banking-safe affordability estimate if agent hasn't set it yet.
    Uses a conservative multiplier to avoid over-approving.
    """
    if "price_cap_est" in state:
        return

    monthly = state.get("monthly_target")
    term = state.get("term_months", 60)
    down = state.get("down_payment", 0)

    try:
        monthly_f = float(monthly) if monthly not in (None, "", []) else 0.0
    except Exception:
        monthly_f = 0.0

    try:
        term_i = int(term) if term not in (None, "", []) else 60
    except Exception:
        term_i = 60

    try:
        down_i = int(down) if down not in (None, "", []) else 0
    except Exception:
        down_i = 0

    # Conservative cap: ~75% of simple payment * term, plus down.
    state["price_cap_est"] = int((monthly_f * term_i) * 0.75 + down_i) if monthly_f else 0


def _get_or_create_plan(user, session: AutoBuyerSession) -> BuyerPlan:
    plan = (
        BuyerPlan.objects
        .filter(user=user, session=session)
        .order_by("-created_at")
        .first()
    )
    if not plan:
        plan = BuyerPlan.objects.create(
            user=user,
            session=session,
            title="Buyer Plan",
            checklist=[
                "Confirm affordability cap & target APR band",
                "Select 3 finalists and book test drives",
                "Run credit pre-qualification & verify income",
                "Negotiate out-the-door price (OTD)",
                "Finalize financing terms and sign documents",
            ],
        )
    return plan


# -----------------------
# Pages
# -----------------------

@login_required
def ai_auto_home(request: HttpRequest):
    if not _ai_enabled():
        return render(request, "banking/disabled.html", status=404)

    session = _get_or_create_session(request.user)
    messages = list(session.messages.all()[:80])

    return render(
        request,
        "banking/ai_auto/home.html",
        {
            "session_id": session.id,
            "messages": messages,
            "state": session.state or {},
        },
    )


@login_required
def ai_auto_shortlist(request: HttpRequest):
    if not _ai_enabled():
        return render(request, "banking/disabled.html", status=404)

    session = _get_or_create_session(request.user)
    recs = (session.state or {}).get("last_recommendations", [])
    return render(
        request,
        "banking/ai_auto/shortlist.html",
        {"session": session, "recommendations": recs},
    )


@login_required
def buyer_plan(request: HttpRequest):
    if not _ai_enabled():
        return render(request, "banking/disabled.html", status=404)

    session = _get_or_create_session(request.user)
    plan = _get_or_create_plan(request.user, session)

    vehicles = list(plan.vehicles.all().order_by("-created_at")[:50])
    return render(
        request,
        "banking/ai_auto/buyer_plan.html",
        {"plan": plan, "session": session, "vehicles": vehicles},
    )


# -----------------------
# APIs
# -----------------------

@require_POST
@login_required
def ai_auto_message_api(request: HttpRequest):
    if not _ai_enabled():
        return JsonResponse({"ok": False, "error": "AI disabled"}, status=404)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    text = (body.get("text") or "").strip()
    if not text:
        return JsonResponse({"ok": False, "error": "Empty message"}, status=400)

    session = _get_or_create_session(request.user)
    AutoBuyerMessage.objects.create(session=session, role="user", content=text)

    result = run_multi_agent(text=text, state=session.state or {})
    session.state = result.state or {}
    session.save(update_fields=["state", "updated_at"])

    AutoBuyerMessage.objects.create(
        session=session,
        role="assistant",
        agent=result.agent,
        content=result.reply,
        payload=result.payload or {},
    )

    return JsonResponse(
        {"ok": True, "reply": result.reply, "payload": result.payload, "state": session.state}
    )


@require_POST
@login_required
def ai_auto_recommend_api(request: HttpRequest):
    if not _ai_enabled():
        return JsonResponse({"ok": False, "error": "AI disabled"}, status=404)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    session = _get_or_create_session(request.user)
    state = session.state or {}

    # Persist form fields into state (banking-grade continuity)
    for key in [
        "monthly_target",
        "down_payment",
        "body_style",
        "condition",
        "term_months",
        "zip_code",
        "annual_income",
        "dti",
    ]:
        if key in body and body[key] not in (None, "", []):
            state[key] = body[key]

    _ensure_price_cap(state)

    session.state = state
    session.save(update_fields=["state", "updated_at"])

    # Credit snapshot (AI Credit bridge)
    credit_payload = {
        "loan_amnt": state.get("price_cap_est", 0),
        "annual_inc": state.get("annual_income"),
        "dti": state.get("dti"),
        "term": f"{state.get('term_months', 60)} months",
        "purpose": "car",
        # optional enrichers if present:
        "int_rate": body.get("int_rate"),
        "emp_length": body.get("emp_length"),
        "home_ownership": body.get("home_ownership"),
        "open_acc": body.get("open_acc"),
        "revol_bal": body.get("revol_bal"),
        "total_acc": body.get("total_acc"),
        "delinq_2yrs": body.get("delinq_2yrs"),
        "pub_rec": body.get("pub_rec"),
    }

    credit_snapshot = fetch_credit_snapshot(request.user, credit_payload)
    if credit_snapshot:
        session.credit_snapshot = credit_snapshot
        state["credit_snapshot"] = credit_snapshot
        session.state = state
        session.save(update_fields=["credit_snapshot", "state", "updated_at"])

    AutoBuyerMessage.objects.create(
        session=session,
        role="user",
        content="[FORM SUBMIT] Generate recommendations",
        payload=body,
    )

    # Run multi-agent matching
    result = run_multi_agent(text="recommend", state=session.state or {})
    session.state = result.state or {}
    session.save(update_fields=["state", "updated_at"])

    AutoBuyerMessage.objects.create(
        session=session,
        role="assistant",
        agent=result.agent,
        content=result.reply,
        payload=result.payload or {},
    )

    return JsonResponse(
        {"ok": True, "reply": result.reply, "payload": result.payload, "state": session.state}
    )


@require_POST
@login_required
def add_vehicle_to_plan_api(request: HttpRequest):
    """
    Adds a selected vehicle from shortlist into the user's Buyer Plan.
    Expects:
      { session_id: <int>, vehicle: {make, model, year, price, badge?, inventory_id?, trim?, meta?} }
    """
    if not _ai_enabled():
        return JsonResponse({"ok": False, "error": "AI disabled"}, status=404)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON payload"}, status=400)

    session_id = body.get("session_id")
    vehicle = body.get("vehicle")

    if not session_id or not vehicle:
        return JsonResponse({"ok": False, "error": "Missing session_id or vehicle"}, status=400)

    session = AutoBuyerSession.objects.filter(id=session_id, user=request.user).first()
    if not session:
        return JsonResponse({"ok": False, "error": "Invalid session"}, status=400)

    plan = _get_or_create_plan(request.user, session)

    required = ["make", "model", "year", "price"]
    missing = [k for k in required if vehicle.get(k) in (None, "", [])]
    if missing:
        return JsonResponse({"ok": False, "error": f"Missing vehicle fields: {', '.join(missing)}"}, status=400)

    # Normalize numeric fields
    try:
        year_i = int(vehicle.get("year"))
    except Exception:
        year_i = None

    try:
        price_i = int(vehicle.get("price"))
    except Exception:
        price_i = None

    BuyerPlanVehicle.objects.create(
        plan=plan,
        make=str(vehicle.get("make")),
        model=str(vehicle.get("model")),
        year=year_i,
        trim=str(vehicle.get("trim") or ""),
        price=price_i,
        badge=str(vehicle.get("badge") or ""),
        inventory_id=vehicle.get("inventory_id"),
        meta=vehicle if isinstance(vehicle, dict) else {},
    )

    return JsonResponse({"ok": True})


# -----------------------
# Buyer Plan PDF export
# -----------------------

@login_required
def buyer_plan_export_pdf(request: HttpRequest):
    if not _ai_enabled():
        return render(request, "banking/disabled.html", status=404)

    session = _get_or_create_session(request.user)
    plan = BuyerPlan.objects.filter(user=request.user, session=session).order_by("-created_at").first()
    if not plan:
        return HttpResponse("No plan found.", status=404)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="buyer_plan.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "AI Auto — Buyer Plan (Executive Brief)")

    c.setFont("Helvetica", 10)
    y = height - 80
    c.drawString(50, y, f"Plan: {plan.title}")
    y -= 16

    snap = session.credit_snapshot or {}
    if snap:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Credit Intelligence Snapshot")
        y -= 14
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Risk Tier: {snap.get('risk_tier')}")
        y -= 12
        c.drawString(60, y, f"Decision: {snap.get('decision')}")
        y -= 12
        c.drawString(60, y, f"APR: {snap.get('apr')}")
        y -= 12
        c.drawString(60, y, f"Max Amount: {snap.get('max_amount')}")
        y -= 18

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Checklist")
    y -= 14
    c.setFont("Helvetica", 10)
    for item in (plan.checklist or []):
        c.drawString(60, y, f"• {item}")
        y -= 12
        if y < 80:
            c.showPage()
            y = height - 50

    vehicles = list(plan.vehicles.all().order_by("-created_at")[:20])
    if vehicles:
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Selected Vehicles")
        y -= 14
        c.setFont("Helvetica", 10)
        for v in vehicles:
            c.drawString(
                60,
                y,
                f"• {v.year or ''} {v.make} {v.model} {v.trim or ''}  |  Badge: {v.badge or ''}  |  Est: {v.price or ''}"
            )
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

    c.showPage()
    c.save()
    return response


# -----------------------
# Inventory endpoints
# -----------------------

@login_required
def inventory_makes(request: HttpRequest):
    return JsonResponse({"ok": True, "makes": nhtsa_makes()[:400]})


@login_required
def inventory_models(request: HttpRequest):
    make = request.GET.get("make", "")
    year = request.GET.get("year")
    year_i = int(year) if year and year.isdigit() else None
    if not make:
        return JsonResponse({"ok": False, "error": "make required"}, status=400)
    return JsonResponse({"ok": True, "models": nhtsa_models(make=make, year=year_i)[:400]})


@login_required
def inventory_trims(request: HttpRequest):
    make = request.GET.get("make", "")
    model = request.GET.get("model", "")
    year = request.GET.get("year")
    year_i = int(year) if year and year.isdigit() else None
    if not make or not model:
        return JsonResponse({"ok": False, "error": "make & model required"}, status=400)
    trims = carquery_trims(make=make, model=model, year=year_i)
    return JsonResponse({"ok": True, "trims": trims})
