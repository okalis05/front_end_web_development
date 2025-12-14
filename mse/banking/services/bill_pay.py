from django.db import transaction
from banking.models import BankAccount, Transaction, Payee, TxnType, TxnStatus
from decimal import Decimal


@transaction.atomic
def pay_bill(account_id: int, payee_id: int, amount: Decimal):
    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero")

    account = BankAccount.objects.select_for_update().get(id=account_id)
    payee = Payee.objects.get(id=payee_id)

    if account.available_balance < amount:
        raise ValueError("Insufficient funds")

    account.balance -= amount
    account.available_balance -= amount
    account.save()

    Transaction.objects.create(
        account=account,
        payee=payee,
        txn_type=TxnType.BILLPAY,
        status=TxnStatus.POSTED,
        amount=amount,
        memo=f"Bill payment to {payee.name}",
    )

    return account
