from __future__ import annotations

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from .models import Organization, Membership, Plan, Product, Order, Subscription
from .decorators import tenant_required, analyst_required, admin_required
from .forms import LuxeLoginForm, LuxeSignupForm, OrgCreateForm
from .services import add_to_cart, compute_order_totals, ensure_subscription, mark_order_paid, audit

# Create your views here.
class StoreLoginView(LoginView):
    template_name = "store/auth_login.html"
    authentication_form = LuxeLoginForm


def signup(request: HttpRequest):
    if request.method == "POST":
        form = LuxeSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome — your executive workspace is ready.")
            return redirect("store:org_switch")
    else:
        form = LuxeSignupForm()
    return render(request, "store/auth_signup.html", {"form": form})


@login_required
def org_switch(request: HttpRequest):
    orgs = Organization.objects.filter(memberships__user=request.user, memberships__is_active=True, is_active=True).distinct()
    if request.method == "POST":
        slug = request.POST.get("org")
        org = Organization.objects.filter(slug=slug, is_active=True).first()
        if not org:
            messages.error(request, "Organization not found.")
            return redirect("store:org_switch")

        ms = Membership.objects.filter(user=request.user, org=org, is_active=True).first()
        if not ms:
            messages.error(request, "You don’t have access to that organization.")
            return redirect("store:org_switch")

        resp = redirect("store:dashboard")
        resp.set_cookie("store_org", org.slug, samesite="Lax")
        return resp

    return render(request, "store/org_switch.html", {"orgs": orgs, "create_form": OrgCreateForm()})


@login_required
def org_create(request: HttpRequest):
    form = OrgCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        org = form.save()
        Membership.objects.create(user=request.user, org=org, role=Membership.OWNER, is_active=True)
        ensure_subscription(org)
        audit(org, request.user, "org_created", {"org": org.slug})
        messages.success(request, "Organization created. Welcome to the Luxe console.")
        resp = redirect("store:dashboard")
        resp.set_cookie("store_org", org.slug, samesite="Lax")
        return resp
    messages.error(request, "Unable to create organization.")
    return redirect("store:org_switch")


@login_required
@tenant_required
def dashboard(request: HttpRequest):
    org = request.store_org
    sub = ensure_subscription(org)

    products_count = Product.objects.filter(org=org, is_active=True).count()
    orders = Order.objects.filter(org=org).order_by("-created_at")[:8]
    ledger = org.ledger.order_by("-created_at")[:8]

    return render(request, "store/dashboard.html", {
        "org": org, "sub": sub,
        "products_count": products_count,
        "orders": orders, "ledger": ledger,
        "membership": request.store_membership
    })


def pricing(request: HttpRequest):
    plans = Plan.objects.filter(is_active=True, is_public=True).order_by("tier")
    return render(request, "store/pricing.html", {"plans": plans})


@login_required
@tenant_required
def catalog(request: HttpRequest):
    org = request.store_org
    products = Product.objects.filter(org=org, is_active=True).order_by("-created_at")
    return render(request, "store/catalog.html", {"org": org, "products": products})


@login_required
@tenant_required
def product_detail(request: HttpRequest, slug: str):
    org = request.store_org
    product = get_object_or_404(Product, org=org, slug=slug, is_active=True)
    return render(request, "store/product_detail.html", {"org": org, "product": product})


@login_required
@tenant_required
def cart(request: HttpRequest):
    org = request.store_org
    order = Order.objects.filter(org=org, user=request.user, status=Order.DRAFT).order_by("-created_at").first()
    if order:
        compute_order_totals(order)
    return render(request, "store/cart.html", {"org": org, "order": order})


@login_required
@tenant_required
def cart_add(request: HttpRequest, product_id: int):
    org = request.store_org
    product = get_object_or_404(Product, org=org, id=product_id, is_active=True)
    qty = int(request.POST.get("qty") or "1")
    add_to_cart(org, request.user, product, max(1, qty))
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect("store:cart")


@login_required
@tenant_required
def checkout(request: HttpRequest):
    org = request.store_org
    order = Order.objects.filter(org=org, user=request.user, status=Order.DRAFT).order_by("-created_at").first()
    if not order or order.total <= 0:
        messages.info(request, "Your cart is empty.")
        return redirect("store:catalog")

    compute_order_totals(order)

    if request.method == "POST":
        # “Works now” mode: simulate payment instantly
        order.status = Order.SUBMITTED
        order.save(update_fields=["status"])
        mark_order_paid(order, actor=request.user, external_payment_id="manual_demo_payment")
        messages.success(request, "Payment confirmed. Executive receipt issued.")
        return redirect("store:invoices")

    return render(request, "store/checkout.html", {"org": org, "order": order})


@login_required
@tenant_required
def billing(request: HttpRequest):
    org = request.store_org
    sub = ensure_subscription(org)
    plans = Plan.objects.filter(is_active=True, is_public=True).order_by("tier")

    if request.method == "POST":
        plan_code = request.POST.get("plan")
        period = request.POST.get("period") or "monthly"
        plan = Plan.objects.filter(code=plan_code, is_active=True).first()
        if plan:
            sub.plan = plan
            sub.billing_period = period if period in ("monthly", "annual") else "monthly"
            sub.status = Subscription.ACTIVE if hasattr(__import__("store.models"), "Subscription") else sub.status  # safe
            sub.save(update_fields=["plan", "billing_period", "status"])
            audit(org, request.user, "plan_changed", {"plan": plan.code, "period": sub.billing_period})
            messages.success(request, f"Plan upgraded to {plan.name} ({sub.billing_period}).")
            return redirect("store:billing")

        messages.error(request, "Plan not found.")
        return redirect("store:billing")

    return render(request, "store/billing.html", {"org": org, "sub": sub, "plans": plans})


@login_required
@tenant_required
@analyst_required
def invoices(request: HttpRequest):
    org = request.store_org
    orders = Order.objects.filter(org=org, status=Order.PAID).order_by("-created_at")[:50]
    return render(request, "store/invoices.html", {"org": org, "orders": orders})


@login_required
@tenant_required
@analyst_required
def audit_log(request: HttpRequest):
    org = request.store_org
    events = org.audit_events.order_by("-created_at")[:80]
    return render(request, "store/audit.html", {"org": org, "events": events})
