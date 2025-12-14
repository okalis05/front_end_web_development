
from __future__ import annotations
import json
import logging
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import SignupForm, LuxuryAuthForm
from .middleware import TenantMiddleware
from .models import (
    Organization, OrgMembership, Plan, Subscription, AuditEvent,
    ROLE_ADMIN, PLAN_BASIC, PLAN_STANDARD, PLAN_PREMIUM
)
from .selectors import get_user_orgs, get_membership
from .services.stripe_service import create_checkout_session, create_billing_portal, handle_webhook

log = logging.getLogger("store")

class StoreLoginView(LoginView):
    template_name = "store/auth/login.html"
    authentication_form = LuxuryAuthForm

def landing(request: HttpRequest):
    return render(request, "store/landing.html")

def pricing(request: HttpRequest):
    plans = Plan.objects.filter(is_active=True).order_by("monthly_price_usd")
    org = TenantMiddleware.get_org(request)
    return render(request, "store/pricing.html", {"plans": plans, "org": org})

def signup(request: HttpRequest):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            org = Organization.objects.create(
                name=form.cleaned_data["org_name"],
                slug=form.cleaned_data["org_slug"],
            )
            OrgMembership.objects.create(org=org, user=user, role=ROLE_ADMIN, is_active=True)

            # default plan rows should exist; if not, seed command can create them
            # set tenant in session for convenience
            request.session["store_tenant"] = org.slug

            AuditEvent.objects.create(org=org, user=user, action="signup", meta={"org": org.slug})

            login(request, user)
            messages.success(request, "Welcome — your luxury SaaS store is ready.")
            return redirect("store:pricing")
    else:
        form = SignupForm()
    return render(request, "store/auth/signup.html", {"form": form})

@login_required
def org_switch(request: HttpRequest):
    orgs = get_user_orgs(request.user)
    if request.method == "POST":
        slug = (request.POST.get("slug") or "").strip()
        if orgs.filter(slug=slug).exists():
            request.session["store_tenant"] = slug
            return redirect("store:dashboard")
        messages.error(request, "You don’t have access to that organization.")
    return render(request, "store/org_switch.html", {"orgs": orgs})

@login_required
def dashboard(request: HttpRequest):
    org = TenantMiddleware.get_org(request)

    if not org:
        messages.error(request, "Please select an organization.")
        return redirect("store:org_switch")

    membership = get_membership(request.user, org)
    if not membership:
        messages.error(request, "You don’t have access to this organization.")
        return redirect("store:org_switch")

    # 🔐 Lock dashboard until subscription exists
    sub = getattr(org, "subscription", None)
    if not sub or not sub.is_active:
        messages.info(request, "Choose a plan to activate your store.")
        return redirect("store:pricing")

    return render(
        request,
        "store/dashboard.html",
        {
            "org": org,
            "membership": membership,
            "sub": sub,
        },
    )
@login_required
def app_dashboard(request):
    ctx = request.store_tenant
    org = ctx.org

    membership = get_membership(request.user, org)

    return render(
        request,
        "store/app/dashboard.html",
        {
            "org": org,
            "membership": membership,
        },
    )


@login_required
def start_checkout(request: HttpRequest, plan_code: str):
    org = TenantMiddleware.get_org(request)
    if not org:
        return redirect("store:org_switch")

    membership = get_membership(request.user, org)
    if not membership or membership.role != ROLE_ADMIN:
        messages.error(request, "Only org admins can manage billing.")
        return redirect("store:dashboard")

    plan = Plan.objects.filter(code=plan_code, is_active=True).first()
    if not plan or not plan.stripe_price_id:
        messages.error(request, "That plan is not available (Stripe price_id missing).")
        return redirect("store:pricing")

    try:
        res = create_checkout_session(org=org, plan=plan, request=request)
        AuditEvent.objects.create(org=org, user=request.user, action="checkout_started", meta={"plan": plan_code})
        return redirect(res.url)
    except Exception as e:
        log.exception("checkout_failed")
        messages.error(request, "Checkout failed. Check server logs.")
        return redirect("store:pricing")

@login_required
def checkout_return(request: HttpRequest):
    return render(request, "store/checkout_return.html", {"status": request.GET.get("status", "")})

@login_required
def billing(request: HttpRequest):
    org = TenantMiddleware.get_org(request)
    if not org:
        return redirect("store:org_switch")
    membership = get_membership(request.user, org)
    if not membership:
        return redirect("store:org_switch")
    sub = getattr(org, "subscription", None)
    return render(request, "store/billing.html", {"org": org, "membership": membership, "sub": sub})

@login_required
def open_portal(request: HttpRequest):
    org = TenantMiddleware.get_org(request)
    if not org:
        return redirect("store:org_switch")
    membership = get_membership(request.user, org)
    if not membership or membership.role != ROLE_ADMIN:
        messages.error(request, "Only org admins can access billing portal.")
        return redirect("store:billing")

    try:
        url = create_billing_portal(org=org, request=request)
        AuditEvent.objects.create(org=org, user=request.user, action="billing_portal_opened")
        return redirect(url)
    except Exception:
        log.exception("portal_failed")
        messages.error(request, "Billing portal failed. Check server logs.")
        return redirect("store:billing")

@login_required
def settings_page(request: HttpRequest):
    org = TenantMiddleware.get_org(request)
    if not org:
        return redirect("store:org_switch")
    membership = get_membership(request.user, org)
    return render(request, "store/settings.html", {"org": org, "membership": membership})

@csrf_exempt
def stripe_webhook(request: HttpRequest):
    """
    Stripe webhook endpoint.
    Add STRIPE_WEBHOOK_SECRET in settings.
    """
    secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        return HttpResponseBadRequest("Missing STRIPE_WEBHOOK_SECRET")

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=secret)
    except Exception as e:
        return HttpResponseBadRequest("Invalid signature")

    try:
        handle_webhook(event)
    except Exception:
        log.exception("webhook_handler_failed")
        return HttpResponse(status=500)

    return HttpResponse(status=200)
