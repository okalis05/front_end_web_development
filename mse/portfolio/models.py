from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# Create your models here.

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("store:category_detail", args=[self.slug])


class MembershipTier(models.Model):
    """
    Represents a membership tier. Stripe price id powers subscriptions.
    """
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    highlight = models.CharField(max_length=255, blank=True)

    # Stripe
    stripe_price_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Stripe Price ID for subscription (e.g. price_xxx).",
    )

    class Meta:
        ordering = ["price_monthly"]

    def __str__(self) -> str:
        return f"{self.name} (${self.price_monthly}/month)"


class Membership(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("canceled", "Canceled"),
        ("incomplete", "Incomplete"),
        ("incomplete_expired", "Incomplete Expired"),
        ("past_due", "Past Due"),
        ("trialing", "Trialing"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    tier = models.ForeignKey(MembershipTier, on_delete=models.PROTECT, related_name="memberships")

    stripe_customer_id = models.CharField(max_length=200, blank=True)
    stripe_subscription_id = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="active")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.user} – {self.tier.name} ({self.status})"

    @property
    def is_active(self) -> bool:
        return self.status in {"active", "trialing", "past_due"} and self.ended_at is None

    def cancel_locally(self) -> None:
        self.status = "canceled"
        self.ended_at = timezone.now()
        self.save(update_fields=["status", "ended_at"])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Public price (non-member)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Optional member price (if blank, falls back to price)
    member_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Plan gating: require membership / tier
    requires_membership = models.BooleanField(default=False)
    required_tier = models.ForeignKey(
        MembershipTier, null=True, blank=True, on_delete=models.SET_NULL, related_name="gated_products"
    )

    # Optional: Stripe product/price IDs for one-time checkout line items
    stripe_product_id = models.CharField(max_length=200, blank=True)
    stripe_price_id = models.CharField(max_length=200, blank=True)

    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])

    def is_allowed_for(self, membership: "Membership | None") -> bool:
        if not self.requires_membership:
            return True
        if membership is None or not membership.is_active:
            return False
        if self.required_tier is None:
            return True
        # Simple gating by price order: required tier must be <= user's tier in ordering
        return membership.tier.price_monthly >= self.required_tier.price_monthly

    def unit_price_for(self, membership: "Membership | None"):
        if membership and membership.is_active and self.member_price is not None:
            return self.member_price
        return self.price


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Stripe reconciliation
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.id}"

    @property
    def items_count(self) -> int:
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # unit price paid

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
