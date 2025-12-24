from django.contrib import admin
from .models import AutoBuyerSession, AutoBuyerMessage

@admin.register(AutoBuyerSession)
class AutoBuyerSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("user__username", "user__email")

@admin.register(AutoBuyerMessage)
class AutoBuyerMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "agent", "created_at")
    list_filter = ("role", "agent", "created_at")
    search_fields = ("content",)
