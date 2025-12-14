
from __future__ import annotations
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
ROLE_ADMIN = "admin"
ROLE_BASIC = "basic"
ROLE_STANDARD = "standard"
ROLE_PREMIUM = "premium"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Admin"),
    (ROLE_BASIC, "Basic"),
    (ROLE_STANDARD, "Standard"),
    (ROLE_PREMIUM, "Premium"),
]

PLAN_BASIC = "basic"
PLAN_STANDARD = "standard"
PLAN_PREMIUM = "premium"

PLAN_CHOICES = [
    (PLAN_BASIC, "Basic"),
    (PLAN_STANDARD, "Standard"),
    (PLAN_PREMIUM, "Premium"),
]

SUB_ACTIVE = "active"
SUB_INCOMPLETE = "incomplete"
SUB_PAST_DUE = "past_due"
SUB_CANCELED = "canceled"
SUB_TRIALING = "trialing"

SUB_STATUS_CHOICES = [
    (SUB_ACTIVE, "Active"),
    (SUB_INCOMPLETE, "Incomplete"),
    (SUB_PAST_DUE, "Past Due"),
    (SUB_CANCELED, "Canceled"),
    (SUB_TRIALING, "Trialing"),
]


class Organization(models.Model):
    """
    Multi-tenant anchor. Single DB, scoped by current tenant (middleware).
    """
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=80, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Stripe mappings
    stripe_customer_id = models.CharField(max_length=255, blank=True, default="")

    # If you want tenant selection by subdomain:
    # tenant.yourdomain.com => slug == tenant
    allow_subdomain_routing = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"


class OrgMembership(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_BASIC)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("org", "user")]
        indexes = [
            models.Index(fields=["org", "user"]),
            models.Index(fields=["user", "role"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.org} ({self.role})"


class Plan(models.Model):
    """
    Represents plan tiers. Stripe price_id binds pricing.
    """
    code = models.CharField(max_length=32, choices=PLAN_CHOICES, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, default="")
    monthly_price_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Stripe Price ID (recurring)
    stripe_price_id = models.CharField(max_length=255, blank=True, default="")

    # Feature flags
    seats_included = models.PositiveIntegerField(default=1)
    api_access = models.BooleanField(default=True)
    priority_support = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Subscription(models.Model):
    """
    One subscription per org (typical SaaS).
    """
    org = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=SUB_STATUS_CHOICES, default=SUB_INCOMPLETE)

    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    # Stripe IDs
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default="")
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, default="")

    cancel_at_period_end = models.BooleanField(default=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.org.slug}: {self.plan.code} ({self.status})"

    @property
    def is_paid(self) -> bool:
        return self.status in {SUB_ACTIVE, SUB_TRIALING}


class AuditEvent(models.Model):
    """
    Lightweight audit trail. Useful for compliance & debugging.
    """
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="audit_events")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=120)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["org", "created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.org.slug} {self.action}"
