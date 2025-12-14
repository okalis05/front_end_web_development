from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import BankAccount, Payee, Transaction, TxnStatus, TxnType


@dataclass(frozen=True)
class ServiceResult:
    ok: bool
    message: str


def _money(x) -> Decimal:
    return Decimal(x).quantize(Decimal("0.01"))


@transaction.atomic
def deposit(account: BankAccount, amount: Decimal, memo: str = "") -> ServiceResult:
    amount = _money(amount)
    account.refresh_from_db(lock=True)
    account.balance = _money(account.balance + amount)
    account.available_balance = _money(account.available_balance + amount)
    account.save(update_fields=["balance", "available_balance"])

    Transaction.objects.create(
        account=account,
        txn_type=TxnType.DEPOSIT,
        status=TxnStatus.POSTED,
        amount=amount,
        memo=memo or "Mobile deposit",
        created_at=timezone.now(),
    )
    return ServiceResult(True, "Deposit posted.")


@transaction.atomic
def withdraw(account: BankAccount, amount: Decimal, memo: str = "") -> ServiceResult:
    amount = _money(amount)
    account.refresh_from_db(lock=True)

    if account.available_balance < amount:
        return ServiceResult(False, "Insufficient available balance.")

    account.balance = _money(account.balance - amount)
    account.available_balance = _money(account.available_balance - amount)
    account.save(update_fields=["balance", "available_balance"])

    Transaction.objects.create(
        account=account,
        txn_type=TxnType.WITHDRAWAL,
        status=TxnStatus.POSTED,
        amount=amount,
        memo=memo or "ATM withdrawal",
        created_at=timezone.now(),
    )
    return ServiceResult(True, "Withdrawal posted.")


@transaction.atomic
def transfer_between_accounts(
    from_account: BankAccount,
    to_account: BankAccount,
    amount: Decimal,
    memo: str = "",
) -> ServiceResult:
    amount = _money(amount)

    if from_account.user_id != to_account.user_id:
        return ServiceResult(False, "Transfers are only allowed between your accounts (demo).")

    if from_account.id == to_account.id:
        return ServiceResult(False, "Choose two different accounts.")

    from_account.refresh_from_db(lock=True)
    to_account.refresh_from_db(lock=True)

    if from_account.available_balance < amount:
        return ServiceResult(False, "Insufficient available balance.")

    from_account.balance = _money(from_account.balance - amount)
    from_account.available_balance = _money(from_account.available_balance - amount)
    to_account.balance = _money(to_account.balance + amount)
    to_account.available_balance = _money(to_account.available_balance + amount)

    from_account.save(update_fields=["balance", "available_balance"])
    to_account.save(update_fields=["balance", "available_balance"])

    Transaction.objects.create(
        account=from_account,
        txn_type=TxnType.TRANSFER_OUT,
        status=TxnStatus.POSTED,
        amount=amount,
        related_account=to_account,
        memo=memo or f"Transfer to ••••{to_account.last4}",
        created_at=timezone.now(),
    )
    Transaction.objects.create(
        account=to_account,
        txn_type=TxnType.TRANSFER_IN,
        status=TxnStatus.POSTED,
        amount=amount,
        related_account=from_account,
        memo=memo or f"Transfer from ••••{from_account.last4}",
        created_at=timezone.now(),
    )

    return ServiceResult(True, "Transfer completed.")


@transaction.atomic
def pay_bill(
    from_account: BankAccount,
    payee: Payee,
    amount: Decimal,
    memo: str = "",
) -> ServiceResult:
    amount = _money(amount)

    if payee.user_id != from_account.user_id:
        return ServiceResult(False, "Invalid payee.")

    from_account.refresh_from_db(lock=True)
    if from_account.available_balance < amount:
        return ServiceResult(False, "Insufficient available balance.")

    from_account.balance = _money(from_account.balance - amount)
    from_account.available_balance = _money(from_account.available_balance - amount)
    from_account.save(update_fields=["balance", "available_balance"])

    Transaction.objects.create(
        account=from_account,
        txn_type=TxnType.BILLPAY,
        status=TxnStatus.POSTED,
        amount=amount,
        payee=payee,
        memo=memo or f"Bill pay • {payee.name}",
        created_at=timezone.now(),
    )
    return ServiceResult(True, "Bill payment sent.")
