from __future__ import annotations

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import BillPayForm, DepositForm, PayeeForm, TransferForm, WithdrawalForm
from .models import BankAccount, Card, Payee, Transaction
from .services import deposit, pay_bill, transfer_between_accounts, withdraw
from .models import ScheduledPayment
from .forms import ScheduledPaymentForm
from datetime import date
from .models import Statement
from .services.statements import generate_statement
from .services import deposit, withdraw, pay_bill



from .services.transfer_between_accounts import transfer_between_accounts



# Create your views here.
def _user_account_or_404(user, public_id: str) -> BankAccount:
    return get_object_or_404(BankAccount, user=user, public_id=public_id, is_active=True)


@login_required
def dashboard(request):
    accounts = BankAccount.objects.filter(user=request.user, is_active=True).order_by("account_type", "id")
    total = accounts.aggregate(s=Sum("balance"))["s"] or Decimal("0.00")

    recent = (
        Transaction.objects.filter(account__user=request.user)
        .select_related("account", "payee", "related_account")
        .order_by("-created_at")[:12]
    )

    # Simple spend aggregation (last 30 days)
    start = timezone.now() - timezone.timedelta(days=30)
    spend = (
        Transaction.objects.filter(
            account__user=request.user,
            created_at__gte=start,
            txn_type__in=["WITHDRAWAL", "BILLPAY", "CARD", "TRANSFER_OUT"],
        )
        .aggregate(s=Sum("amount"))["s"]
        or Decimal("0.00")
    )

    ctx = {
        "accounts": accounts,
        "total": total,
        "recent": recent,
        "spend_30": spend,
    }
    return render(request, "banking/dashboard.html", ctx)


@login_required
def accounts(request):
    accounts = BankAccount.objects.filter(user=request.user, is_active=True).order_by("account_type", "id")
    return render(request, "banking/accounts.html", {"accounts": accounts})


@login_required
def account_detail(request, public_id: str):
    account = _user_account_or_404(request.user, public_id)
    qs = Transaction.objects.filter(account=account).select_related("payee", "related_account")

    # Filters
    t = request.GET.get("t", "").strip()
    q = request.GET.get("q", "").strip()
    if t:
        qs = qs.filter(txn_type=t)
    if q:
        qs = qs.filter(memo__icontains=q) | qs.filter(merchant__icontains=q)

    txns = qs[:80]
    return render(request, "banking/account_detail.html", {"account": account, "txns": txns})


@login_required
def transfer(request):
    if request.method == "POST":
        form = TransferForm(request.POST, user=request.user)
        if form.is_valid():
            res = transfer_between_accounts(
                form.cleaned_data["from_account"],
                form.cleaned_data["to_account"],
                form.cleaned_data["amount"],
                form.cleaned_data.get("memo", ""),
            )
            if res.ok:
                messages.success(request, res.message)
                return redirect("banking:dashboard")
            messages.error(request, res.message)
    else:
        form = TransferForm(user=request.user)
    return render(request, "banking/transfer.html", {"form": form})


@login_required
def quick_cash(request):
    # Deposit + withdraw in one page via modal buttons (JS triggers)
    deposit_form = DepositForm(user=request.user)
    withdraw_form = WithdrawalForm(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "deposit":
            deposit_form = DepositForm(request.POST, user=request.user)
            if deposit_form.is_valid():
                res = deposit(
                    deposit_form.cleaned_data["account"],
                    deposit_form.cleaned_data["amount"],
                    deposit_form.cleaned_data.get("memo", ""),
                )
                (messages.success if res.ok else messages.error)(request, res.message)
                return redirect("banking:quick_cash")

        if action == "withdraw":
            withdraw_form = WithdrawalForm(request.POST, user=request.user)
            if withdraw_form.is_valid():
                res = withdraw(
                    withdraw_form.cleaned_data["account"],
                    withdraw_form.cleaned_data["amount"],
                    withdraw_form.cleaned_data.get("memo", ""),
                )
                (messages.success if res.ok else messages.error)(request, res.message)
                return redirect("banking:quick_cash")

    return render(
        request,
        "banking/settings.html",
        {"deposit_form": deposit_form, "withdraw_form": withdraw_form},
    )


@login_required
def billpay(request):
    payees = Payee.objects.filter(user=request.user, is_active=True).order_by("name")

    # Create payee
    if request.method == "POST" and request.POST.get("action") == "add_payee":
        pf = PayeeForm(request.POST)
        if pf.is_valid():
            payee = pf.save(commit=False)
            payee.user = request.user
            payee.save()
            messages.success(request, "Payee added.")
            return redirect("banking:billpay")
        messages.error(request, "Please correct the payee form.")
        return render(request, "banking/billpay.html", {"payees": payees, "payee_form": pf, "bill_form": BillPayForm(user=request.user)})

    # Send payment
    if request.method == "POST" and request.POST.get("action") == "pay_bill":
        bf = BillPayForm(request.POST, user=request.user)
        if bf.is_valid():
            res = pay_bill(
                bf.cleaned_data["from_account"],
                bf.cleaned_data["payee"],
                bf.cleaned_data["amount"],
                bf.cleaned_data.get("memo", ""),
            )
            (messages.success if res.ok else messages.error)(request, res.message)
            return redirect("banking:billpay")
        messages.error(request, "Please correct the payment form.")
        return render(request, "banking/billpay.html", {"payees": payees, "payee_form": PayeeForm(), "bill_form": bf})

    return render(
        request,
        "banking/billpay.html",
        {
            "payees": payees,
            "payee_form": PayeeForm(),
            "bill_form": BillPayForm(user=request.user),
        },
    )


@login_required
def cards(request):
    cards = Card.objects.filter(user=request.user).select_related("linked_account").order_by("-created_at")
    if request.method == "POST":
        card_id = request.POST.get("card_id")
        action = request.POST.get("action")
        card = get_object_or_404(Card, id=card_id, user=request.user)
        if action == "toggle_freeze":
            card.status = "FROZEN" if card.status == "ACTIVE" else "ACTIVE"
            card.save(update_fields=["status"])
            messages.success(request, "Card status updated.")
        return redirect("banking:cards")
    return render(request, "banking/cards.html", {"cards": cards})


@login_required
def export_transactions_csv(request, public_id: str):
    account = _user_account_or_404(request.user, public_id)
    txns = Transaction.objects.filter(account=account).select_related("payee", "related_account").order_by("-created_at")[:500]

    lines = ["date,type,status,amount,memo,merchant,payee,related_account"]
    for t in txns:
        lines.append(
            ",".join(
                [
                    t.created_at.strftime("%Y-%m-%d %H:%M"),
                    t.txn_type,
                    t.status,
                    f"{t.amount}",
                    (t.memo or "").replace(",", " "),
                    (t.merchant or "").replace(",", " "),
                    (t.payee.name if t.payee else "").replace(",", " "),
                    (t.related_account.public_id if t.related_account else ""),
                ]
            )
        )
    data = "\n".join(lines)
    resp = HttpResponse(data, content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="{account.public_id}_transactions.csv"'
    return resp


@login_required
def scheduled_payments(request):
    payments = ScheduledPayment.objects.filter(
        user=request.user
    ).select_related("account", "payee").order_by("next_run")

    if request.method == "POST":
        action = request.POST.get("action")

        # Create new scheduled payment
        if action == "create":
            form = ScheduledPaymentForm(request.POST, user=request.user)
            if form.is_valid():
                sp = form.save(commit=False)
                sp.user = request.user
                sp.save()
                messages.success(request, "Scheduled payment created.")
                return redirect("banking:scheduled")
            messages.error(request, "Please correct the form.")

        # Toggle active / paused
        elif action == "toggle":
            sp = get_object_or_404(
                ScheduledPayment,
                id=request.POST.get("payment_id"),
                user=request.user,
            )
            sp.active = not sp.active
            sp.save(update_fields=["active"])
            messages.success(request, "Payment status updated.")
            return redirect("banking:scheduled")

        # Delete
        elif action == "delete":
            sp = get_object_or_404(
                ScheduledPayment,
                id=request.POST.get("payment_id"),
                user=request.user,
            )
            sp.delete()
            messages.success(request, "Scheduled payment deleted.")
            return redirect("banking:scheduled")

    else:
        form = ScheduledPaymentForm(user=request.user)

    return render(
        request,
        "banking/scheduled.html",
        {
            "payments": payments,
            "form": form,
        },
    )


@login_required
def statements(request):
    accounts = BankAccount.objects.filter(user=request.user)
    statements = Statement.objects.filter(account__user=request.user)

    if request.method == "POST":
        account_id = request.POST.get("account")
        month = request.POST.get("month")

        account = get_object_or_404(BankAccount, id=account_id, user=request.user)
        month_date = date.fromisoformat(month + "-01")

        pdf = generate_statement(account, month_date)

        stmt, _ = Statement.objects.get_or_create(
            account=account,
            month=month_date,
        )
        stmt.pdf.save(f"{account.public_id}_{month}.pdf", pdf)
        stmt.save()

        messages.success(request, "Statement generated.")
        return redirect("banking:statements")

    return render(
        request,
        "banking/statements.html",
        {"accounts": accounts, "statements": statements},
    )

@login_required
def card_activity(request):
    txns = Transaction.objects.filter(
        account__cards__user=request.user,
        txn_type="CARD"
    ).select_related("account").order_by("-created_at")

    return render(
        request,
        "banking/banking_activity.html",
        {"transactions": txns},
    )
@login_required
def spending(request):
    data = (
        Transaction.objects.filter(account__user=request.user)
        .values("merchant")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    return render(
        request,
        "banking/spending.html",
        {"data": data},
    )
