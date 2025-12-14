from __future__ import annotations

from decimal import Decimal
from django import forms
from django.core.validators import MinValueValidator

from .models import BankAccount, Payee


class AmountField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", 14)
        kwargs.setdefault("decimal_places", 2)
        kwargs.setdefault("validators", [MinValueValidator(Decimal("0.01"))])
        super().__init__(*args, **kwargs)


class DepositForm(forms.Form):
    account = forms.ModelChoiceField(queryset=BankAccount.objects.none())
    amount = AmountField()
    memo = forms.CharField(required=False, max_length=140)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = BankAccount.objects.filter(user=user, is_active=True)


class WithdrawalForm(forms.Form):
    account = forms.ModelChoiceField(queryset=BankAccount.objects.none())
    amount = AmountField()
    memo = forms.CharField(required=False, max_length=140)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = BankAccount.objects.filter(user=user, is_active=True)


class TransferForm(forms.Form):
    from_account = forms.ModelChoiceField(queryset=BankAccount.objects.none())
    to_account = forms.ModelChoiceField(queryset=BankAccount.objects.none())
    amount = AmountField()
    memo = forms.CharField(required=False, max_length=140)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = BankAccount.objects.filter(user=user, is_active=True)
        self.fields["from_account"].queryset = qs
        self.fields["to_account"].queryset = qs


class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ["name", "category", "account_hint"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Verizon, Rent, Electric"}),
            "category": forms.TextInput(attrs={"placeholder": "Bills"}),
            "account_hint": forms.TextInput(attrs={"placeholder": "Optional note for you"}),
        }


class BillPayForm(forms.Form):
    from_account = forms.ModelChoiceField(queryset=BankAccount.objects.none())
    payee = forms.ModelChoiceField(queryset=Payee.objects.none())
    amount = AmountField()
    memo = forms.CharField(required=False, max_length=140)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["from_account"].queryset = BankAccount.objects.filter(user=user, is_active=True)
        self.fields["payee"].queryset = Payee.objects.filter(user=user, is_active=True).order_by("name")

from .models import ScheduledPayment, Payee, BankAccount

class ScheduledPaymentForm(forms.ModelForm):
    class Meta:
        model = ScheduledPayment
        fields = ["account", "payee", "amount", "frequency", "next_run"]
        widgets = {
            "next_run": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = BankAccount.objects.filter(
            user=user, is_active=True
        )
        self.fields["payee"].queryset = Payee.objects.filter(
            user=user, is_active=True
        )

