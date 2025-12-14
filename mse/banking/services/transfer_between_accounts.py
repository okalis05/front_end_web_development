from django.db import transaction
from banking.models import BankAccount, Transaction, TxnType, TxnStatus
from decimal import Decimal


@transaction.atomic
def transfer_between_accounts(
    from_account_id: int,
    to_account_id: int,
    amount: Decimal,
):
    if amount <= 0:
        raise ValueError("Transfer amount must be greater than zero")

    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer to the same account")

    from_account = BankAccount.objects.select_for_update().get(id=from_account_id)
    to_account = BankAccount.objects.select_for_update().get(id=to_account_id)

    if from_account.available_balance < amount:
        raise ValueError("Insufficient funds")

    from_account.balance -= amount
    from_account.available_balance -= amount

    to_account.balance += amount
    to_account.available_balance += amount

    from_account.save()
    to_account.save()

    Transaction.objects.create(
        account=from_account,
        related_account=to_account,
        txn_type=TxnType.TRANSFER_OUT,
        status=TxnStatus.POSTED,
        amount=amount,
        memo=f"Transfer to {to_account.public_id}",
    )

    Transaction.objects.create(
        account=to_account,
        related_account=from_account,
        txn_type=TxnType.TRANSFER_IN,
        status=TxnStatus.POSTED,
        amount=amount,
        memo=f"Transfer from {from_account.public_id}",
    )

    return from_account, to_account
