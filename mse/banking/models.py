from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class AccountType(models.TextChoices):
    CHECKING = "CHECKING", "Checking"
    SAVINGS = "SAVINGS", "Savings"
    CREDIT = "CREDIT", "Credit (demo)"


class TxnType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Deposit"
    WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
    TRANSFER_IN = "TRANSFER_IN", "Transfer In"
    TRANSFER_OUT = "TRANSFER_OUT", "Transfer Out"
    BILLPAY = "BILLPAY", "Bill Payment"
    CARD = "CARD", "Card Purchase"


class TxnStatus(models.TextChoices):
    POSTED = "POSTED", "Posted"
    PENDING = "PENDING", "Pending"
    FAILED = "FAILED", "Failed"


class BankAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_accounts")
    nickname = models.CharField(max_length=48, blank=True, default="")
    account_type = models.CharField(max_length=16, choices=AccountType.choices, default=AccountType.CHECKING)
    # For demo/UI only (NOT real bank numbers)
    public_id = models.CharField(max_length=12, unique=True)  # e.g. "ACCT-9F3K2M"
    last4 = models.CharField(max_length=4)

    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    available_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["user", "account_type"]),
            models.Index(fields=["public_id"]),
        ]

    def __str__(self) -> str:
        name = self.nickname or self.get_account_type_display()
        return f"{name} ••••{self.last4} ({self.user})"


class Payee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_payees")
    name = models.CharField(max_length=80)
    category = models.CharField(max_length=40, blank=True, default="Bills")
    account_hint = models.CharField(max_length=32, blank=True, default="")  # UI hint
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("user", "name")]

    def __str__(self) -> str:
        return f"{self.name} ({self.user})"


class Transaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="transactions")
    txn_type = models.CharField(max_length=16, choices=TxnType.choices)
    status = models.CharField(max_length=12, choices=TxnStatus.choices, default=TxnStatus.POSTED)

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    # Optional links (for transfers / billpay)
    related_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_transactions",
    )
    payee = models.ForeignKey(Payee, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")

    memo = models.CharField(max_length=140, blank=True, default="")
    merchant = models.CharField(max_length=80, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["account", "created_at"]),
            models.Index(fields=["txn_type", "status"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(amount__gt=0), name="txn_amount_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.txn_type} {self.amount} ({self.account.public_id})"


class CardStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    FROZEN = "FROZEN", "Frozen"
    CLOSED = "CLOSED", "Closed"


class Card(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_cards")
    linked_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="cards")

    display_name = models.CharField(max_length=32, default="Platinum")
    brand = models.CharField(max_length=16, default="VISA")
    last4 = models.CharField(max_length=4)

    status = models.CharField(max_length=10, choices=CardStatus.choices, default=CardStatus.ACTIVE)
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1500.00"))
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ••••{self.last4} ({self.user})"
    

class ScheduledPayment(models.Model):
    FREQUENCY_CHOICES = [
        ("ONCE", "One-time"),
        ("MONTHLY", "Monthly"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.ForeignKey("BankAccount", on_delete=models.CASCADE)
    payee = models.ForeignKey("Payee", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    next_run = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.payee} ({self.frequency})"
    
    
class BankingOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at


class Statement(models.Model):
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="statements",
    )
    period_start = models.DateField()
    period_end = models.DateField()

    opening_balance = models.DecimalField(max_digits=14, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=14, decimal_places=2)

    generated_at = models.DateTimeField(default=timezone.now)
    pdf_file = models.FileField(upload_to="statements/", blank=True, null=True)

    class Meta:
        unique_together = [("account", "period_start", "period_end")]
        ordering = ["-period_end"]

    def __str__(self):
        return f"Statement {self.period_start} → {self.period_end} ({self.account.public_id})"
