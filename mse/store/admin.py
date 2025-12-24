from django.contrib import admin
from .models import (
    Organization, Membership, Plan, Subscription,
    Product, Order, OrderItem, LedgerEntry, AuditEvent
)


# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "risk_tier", "country", "created_at")
    search_fields = ("name", "slug")

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "org", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tier", "monthly_price", "annual_price", "is_public", "is_active")
    list_filter = ("is_public", "is_active")
    search_fields = ("name", "code")

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("org", "plan", "status", "billing_period", "current_period_end")
    list_filter = ("status", "billing_period")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "price", "accent", "is_active", "created_at")
    list_filter = ("accent", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "org", "user", "status", "total", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("org", "direction", "amount", "currency", "event_code", "created_at")
    list_filter = ("event_code",)

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("org", "action", "actor", "created_at")
    list_filter = ("action",)
