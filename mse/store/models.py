# Dependencies
from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


User = settings.AUTH_USER_MODEL

# Create your models here
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TimeStampedModel):
    name = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)

    # “Fintech” touch: compliance / metadata
    legal_name = models.CharField(max_length=220, blank=True)
    country = models.CharField(max_length=2, blank=True)  # ISO-2
    risk_tier = models.CharField(max_length=24, default="standard")  # standard/high
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Membership(TimeStampedModel):
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    MEMBER = "member"

    ROLE_CHOICES = [
        (OWNER, "Owner"),
        (ADMIN, "Admin"),
        (ANALYST, "Analyst"),
        (MEMBER, "Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store_memberships")
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("user", "org")]
        indexes = [models.Index(fields=["org", "role", "is_active"])]

    def __str__(self) -> str:
        return f"{self.user} @ {self.org} ({self.role})"


class Plan(TimeStampedModel):
    # You can map this to Stripe price_id or run manual mode.
    name = models.CharField(max_length=80)
    code = models.SlugField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=8, default="USD")

    stripe_monthly_price_id = models.CharField(max_length=120, blank=True)
    stripe_annual_price_id = models.CharField(max_length=120, blank=True)

    # Executive toggles
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    tier = models.PositiveSmallIntegerField(default=1)  # 1..N

    def __str__(self) -> str:
        return self.name


class Subscription(TimeStampedModel):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (TRIALING, "Trialing"),
        (ACTIVE, "Active"),
        (PAST_DUE, "Past Due"),
        (CANCELED, "Canceled"),
    ]

    org = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TRIALING)
    billing_period = models.CharField(max_length=16, default="monthly")  # monthly/annual
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    # Stripe identifiers
    stripe_customer_id = models.CharField(max_length=120, blank=True)
    stripe_subscription_id = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"{self.org} → {self.plan} ({self.status})"


class Product(TimeStampedModel):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=8, default="USD")
    is_active = models.BooleanField(default=True)

    accent = models.CharField(max_length=32, default="purple")  # purple/gold/red
    image_url = models.URLField(blank=True)

    class Meta:
        unique_together = [("org", "slug")]
        indexes = [models.Index(fields=["org", "is_active"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.org})"


class Order(TimeStampedModel):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (SUBMITTED, "Submitted"),
        (PAID, "Paid"),
        (FAILED, "Failed"),
        (CANCELED, "Canceled"),
    ]

    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="orders")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    currency = models.CharField(max_length=8, default="USD")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    external_payment_id = models.CharField(max_length=140, blank=True)
    failure_reason = models.CharField(max_length=220, blank=True)

    def __str__(self) -> str:
        return f"Order {self.id} ({self.org}) {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        indexes = [models.Index(fields=["order"])]

    def __str__(self) -> str:
        return f"{self.product} x{self.qty}"


class LedgerEntry(TimeStampedModel):
    """
    Fintech-grade: minimal ledger lines for auditing money movement.
    """
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="ledger")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    direction = models.CharField(max_length=8, default="credit")  # credit/debit
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=8, default="USD")
    memo = models.CharField(max_length=220, blank=True)
    event_code = models.CharField(max_length=80, default="order_payment")

    class Meta:
        indexes = [models.Index(fields=["org", "created_at", "event_code"])]

    def __str__(self) -> str:
        return f"{self.org}: {self.direction} {self.amount} {self.currency}"


class AuditEvent(TimeStampedModel):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="audit_events")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=80)
    detail = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["org", "created_at", "action"])]

    def __str__(self) -> str:
        return f"{self.org} {self.action} @ {self.created_at:%Y-%m-%d}"
