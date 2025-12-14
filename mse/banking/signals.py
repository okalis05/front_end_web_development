from __future__ import annotations

import secrets
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BankAccount, Card, AccountType


def _new_public_id() -> str:
    return "ACCT-" + secrets.token_hex(3).upper()  # 6 hex chars


def _last4() -> str:
    return str(secrets.randbelow(10000)).zfill(4)


@receiver(post_save, sender=get_user_model())
def create_default_banking(sender, instance, created, **kwargs):
    if not created:
        return

    # Create a demo Checking + Savings + one Card (scoped to this app only)
    checking = BankAccount.objects.create(
        user=instance,
        account_type=AccountType.CHECKING,
        nickname="Everyday Checking",
        public_id=_new_public_id(),
        last4=_last4(),
        balance=Decimal("1250.00"),
        available_balance=Decimal("1250.00"),
    )
    savings = BankAccount.objects.create(
        user=instance,
        account_type=AccountType.SAVINGS,
        nickname="High-Yield Savings",
        public_id=_new_public_id(),
        last4=_last4(),
        balance=Decimal("5200.00"),
        available_balance=Decimal("5200.00"),
    )

    Card.objects.create(
        user=instance,
        linked_account=checking,
        display_name="Gold Elite",
        brand="VISA",
        last4=_last4(),
    )
