from __future__ import annotations
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from banking.ai_auto.models import AutoBuyerSession, AutoBuyerMessage
from banking.ai_credit.models import CreditApplication, CreditModelArtifact

@login_required
def ai_portfolio_dashboard(request):
    auto_sessions = AutoBuyerSession.objects.count()
    auto_active = AutoBuyerSession.objects.filter(is_active=True).count()
    auto_messages = AutoBuyerMessage.objects.count()

    credit_apps = CreditApplication.objects.count()
    low = CreditApplication.objects.filter(risk_tier="LOW").count()
    medium = CreditApplication.objects.filter(risk_tier="MEDIUM").count()
    high = CreditApplication.objects.filter(risk_tier="HIGH").count()

    model = CreditModelArtifact.objects.filter(is_active=True).order_by("-created_at").first()
    recent = CreditApplication.objects.order_by("-created_at")[:20]

    return render(request, "banking/dashboards/ai_portfolio.html", {
        "kpi": {
            "auto_sessions": auto_sessions,
            "auto_active": auto_active,
            "auto_messages": auto_messages,
            "credit_apps": credit_apps,
            "low": low, "medium": medium, "high": high,
        },
        "model": model,
        "recent": recent,
    })
