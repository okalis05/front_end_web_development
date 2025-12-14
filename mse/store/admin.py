from django.contrib import admin
from django.contrib import admin
from .models import Organization, OrgMembership, Plan, Subscription, AuditEvent

# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "stripe_customer_id", "created_at")
    search_fields = ("name", "slug")

@admin.register(OrgMembership)
class OrgMembershipAdmin(admin.ModelAdmin):
    list_display = ("org", "user", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active")
    search_fields = ("org__name", "org__slug", "user__username", "user__email")

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "monthly_price_usd", "stripe_price_id", "api_access", "priority_support", "is_active")
    list_filter = ("is_active", "api_access", "priority_support")
    search_fields = ("code", "name")

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("org", "plan", "status", "cancel_at_period_end", "current_period_end", "updated_at")
    list_filter = ("status", "cancel_at_period_end")
    search_fields = ("org__slug", "stripe_subscription_id")

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "org", "user", "action")
    search_fields = ("org__slug", "action", "user__username")
    list_filter = ("action",)
