from __future__ import annotations
import stripe
from dataclasses import dataclass
from typing import Optional
from django.conf import settings
from django.urls import reverse

from ..models import Organization, Plan, Subscription, SUB_ACTIVE, SUB_TRIALING, SUB_CANCELED

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)

@dataclass
class CheckoutResult:
    url: str
    session_id: str

def ensure_customer(org: Organization) -> str:
    if org.stripe_customer_id:
        return org.stripe_customer_id
    customer = stripe.Customer.create(
        name=org.name,
        metadata={"org_slug": org.slug},
    )
    org.stripe_customer_id = customer["id"]
    org.save(update_fields=["stripe_customer_id"])
    return org.stripe_customer_id

def create_checkout_session(*, org: Organization, plan: Plan, request) -> CheckoutResult:
    customer_id = ensure_customer(org)

    success_url = request.build_absolute_uri(reverse("store:checkout_return")) + "?status=success"
    cancel_url = request.build_absolute_uri(reverse("store:pricing")) + "?status=cancel"

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
        allow_promotion_codes=True,
        success_url=success_url,
        cancel_url=cancel_url,
        automatic_tax={"enabled": True},
        client_reference_id=org.slug,
        subscription_data={"metadata": {"org_slug": org.slug, "plan_code": plan.code}},
        metadata={"org_slug": org.slug, "plan_code": plan.code},
    )

    # persist a local subscription stub
    sub, _ = Subscription.objects.get_or_create(org=org, defaults={"plan": plan})
    sub.plan = plan
    sub.stripe_checkout_session_id = session["id"]
    sub.save(update_fields=["plan", "stripe_checkout_session_id", "updated_at"])

    return CheckoutResult(url=session["url"], session_id=session["id"])

def create_billing_portal(*, org: Organization, request) -> str:
    customer_id = ensure_customer(org)
    return_url = request.build_absolute_uri(reverse("store:billing"))
    portal = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return portal["url"]

def handle_webhook(event: stripe.Event) -> None:
    etype = event["type"]
    data = event["data"]["object"]

    # Checkout complete -> subscription created
    if etype == "checkout.session.completed":
        org_slug = (data.get("metadata") or {}).get("org_slug") or data.get("client_reference_id")
        if not org_slug:
            return
        from ..models import Organization
        try:
            org = Organization.objects.get(slug=org_slug)
        except Organization.DoesNotExist:
            return

        # session has subscription id
        stripe_sub_id = data.get("subscription", "")
        if not stripe_sub_id:
            return

        sub, _ = Subscription.objects.get_or_create(org=org, defaults={"plan": Plan.objects.first()})
        sub.stripe_subscription_id = stripe_sub_id
        sub.status = SUB_ACTIVE  # will be corrected by subscription.updated too
        sub.save(update_fields=["stripe_subscription_id", "status", "updated_at"])
        return

    # Subscription updates
    if etype in {"customer.subscription.updated", "customer.subscription.created"}:
        org_slug = (data.get("metadata") or {}).get("org_slug")
        if not org_slug:
            return
        from ..models import Organization
        try:
            org = Organization.objects.get(slug=org_slug)
        except Organization.DoesNotExist:
            return

        stripe_sub_id = data.get("id", "")
        status = data.get("status", "")
        cps = data.get("current_period_start")
        cpe = data.get("current_period_end")

        plan_code = (data.get("metadata") or {}).get("plan_code", "")
        plan = None
        if plan_code:
            plan = Plan.objects.filter(code=plan_code).first()

        sub, _ = Subscription.objects.get_or_create(org=org, defaults={"plan": plan or Plan.objects.first()})
        if plan:
            sub.plan = plan
        sub.stripe_subscription_id = stripe_sub_id
        sub.status = status or sub.status
        if cps:
            from django.utils import timezone
            sub.current_period_start = timezone.datetime.fromtimestamp(int(cps), tz=timezone.utc)
        if cpe:
            from django.utils import timezone
            sub.current_period_end = timezone.datetime.fromtimestamp(int(cpe), tz=timezone.utc)
        sub.save()
        return

    if etype == "customer.subscription.deleted":
        org_slug = (data.get("metadata") or {}).get("org_slug")
        if not org_slug:
            return
        from ..models import Organization
        try:
            org = Organization.objects.get(slug=org_slug)
        except Organization.DoesNotExist:
            return
        sub = getattr(org, "subscription", None)
        if sub:
            sub.status = SUB_CANCELED
            sub.save(update_fields=["status", "updated_at"])
