from __future__ import annotations

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from banking.models import BankAccount, AccountType


class Command(BaseCommand):
    help = "Create default banking accounts for existing users who don't have any."

    def handle(self, *args, **options):
        User = get_user_model()
        created_count = 0
        for u in User.objects.all():
            if BankAccount.objects.filter(user=u).exists():
                continue
            BankAccount.objects.create(
                user=u,
                account_type=AccountType.CHECKING,
                nickname="Everyday Checking",
                public_id=f"ACCT-SEED{u.id:04d}",
                last4=str(1000 + (u.id % 9000)).zfill(4),
                balance=Decimal("500.00"),
                available_balance=Decimal("500.00"),
            )
            BankAccount.objects.create(
                user=u,
                account_type=AccountType.SAVINGS,
                nickname="High-Yield Savings",
                public_id=f"ACCT-SEED{u.id:04d}S",
                last4=str(2000 + (u.id % 9000)).zfill(4),
                balance=Decimal("2500.00"),
                available_balance=Decimal("2500.00"),
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Users initialized: {created_count}"))
