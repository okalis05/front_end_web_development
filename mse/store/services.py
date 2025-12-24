from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import (
    Organization, Plan, Subscription, Product, Order, OrderItem, LedgerEntry, AuditEvent
)

def audit(org: Organization, actor, action: str, detail: dict | None = None):
    AuditEvent.objects.create(org=org, actor=actor if getattr(actor, "is_authenticated", False) else None,
                              action=action, detail=detail or {})

def ensure_subscription(org: Organization) -> Subscription:
    sub = getattr(org, "subscription", None)
    if sub:
        return sub
    # default plan: first active public plan
    plan = Plan.objects.filter(is_active=True, is_public=True).order_by("tier").first()
    if not plan:
        plan = Plan.objects.create(name="Luxe Starter", code="luxe-starter", monthly_price=Decimal("0.00"), annual_price=Decimal("0.00"))
    return Subscription.objects.create(
        org=org,
        plan=plan,
        status=Subscription.TRIALING,
        billing_period="monthly",
        trial_ends_at=timezone.now() + timezone.timedelta(days=14),
        current_period_end=timezone.now() + timezone.timedelta(days=14),
    )

def compute_order_totals(order: Order) -> Order:
    subtotal = Decimal("0.00")
    for item in order.items.all():
        item.line_total = (item.unit_price * item.qty).quantize(Decimal("0.01"))
        item.save(update_fields=["line_total"])
        subtotal += item.line_total

    tax = (subtotal * Decimal("0.00")).quantize(Decimal("0.01"))  # extend later
    total = (subtotal + tax).quantize(Decimal("0.01"))

    order.subtotal = subtotal
    order.tax = tax
    order.total = total
    order.save(update_fields=["subtotal", "tax", "total"])
    return order

@transaction.atomic
def add_to_cart(org: Organization, user, product: Product, qty: int = 1) -> Order:
    order, _ = Order.objects.get_or_create(org=org, user=user, status=Order.DRAFT, defaults={"currency": product.currency})
    item = order.items.filter(product=product).first()
    if item:
        item.qty += qty
        item.save(update_fields=["qty"])
    else:
        OrderItem.objects.create(order=order, product=product, qty=qty, unit_price=product.price, line_total=Decimal("0.00"))
    compute_order_totals(order)
    return order

@transaction.atomic
def mark_order_paid(order: Order, actor=None, external_payment_id: str = "") -> Order:
    if order.status == Order.PAID:
        return order
    order.status = Order.PAID
    order.external_payment_id = external_payment_id
    order.save(update_fields=["status", "external_payment_id"])

    LedgerEntry.objects.create(
        org=order.org, order=order, direction="credit",
        amount=order.total, currency=order.currency,
        memo=f"Order {order.id} payment", event_code="order_paid"
    )
    audit(order.org, actor, "order_paid", {"order_id": order.id, "total": str(order.total)})
    return order

def stripe_enabled() -> bool:
    return bool(getattr(settings, "STORE_STRIPE_ENABLED", False))
