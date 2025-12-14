from django.db import transaction
from banking.models import BankAccount, Transaction, TxnType, TxnStatus
from decimal import Decimal


@transaction.atomic
def withdraw(account_id: int, amount: Decimal, memo="Withdrawal"):
    if amount <= 0:
        raise ValueError("Withdrawal amount must be greater than zero")

    account = BankAccount.objects.select_for_update().get(id=account_id)

    if account.available_balance < amount:
        raise ValueError("Insufficient funds")

    account.balance -= amount
    account.available_balance -= amount
    account.save()

    Transaction.objects.create(
        account=account,
        txn_type=TxnType.WITHDRAWAL,
        status=TxnStatus.POSTED,
        amount=amount,
        memo=memo,
    )

    return account
