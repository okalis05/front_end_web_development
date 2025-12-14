from django.db import transaction
from banking.models import BankAccount, Transaction, TxnType, TxnStatus
from decimal import Decimal


@transaction.atomic
def deposit(account_id: int, amount: Decimal, memo="Deposit"):
    if amount <= 0:
        raise ValueError("Deposit amount must be greater than zero")

    account = BankAccount.objects.select_for_update().get(id=account_id)

    account.balance += amount
    account.available_balance += amount
    account.save()

    Transaction.objects.create(
        account=account,
        txn_type=TxnType.DEPOSIT,
        status=TxnStatus.POSTED,
        amount=amount,
        memo=memo,
    )

    return account
