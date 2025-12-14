from django.contrib import admin
from django.contrib import admin
from .models import BankAccount, Card, Payee, Transaction



# Register your models here.
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("public_id", "user", "account_type", "nickname", "last4", "balance", "available_balance", "is_active")
    search_fields = ("public_id", "user__username", "nickname", "last4")
    list_filter = ("account_type", "is_active")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "account", "txn_type", "status", "amount", "payee", "related_account", "memo")
    search_fields = ("account__public_id", "memo", "merchant", "payee__name")
    list_filter = ("txn_type", "status")


@admin.register(Payee)
class PayeeAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category", "is_active")
    search_fields = ("name", "user__username", "category")
    list_filter = ("is_active", "category")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("display_name", "brand", "last4", "user", "linked_account", "status", "daily_limit")
    search_fields = ("user__username", "last4", "display_name")
    list_filter = ("status", "brand")
