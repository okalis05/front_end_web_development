from django.contrib import admin
from .models import Metric, Event



# Register your models here.
@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ("industry_key", "kpi_key", "value", "ts")
    list_filter = ("industry_key", "kpi_key")
    search_fields = ("industry_key", "kpi_key")
    ordering = ("-ts",)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("industry_key", "event_type", "severity", "title", "kpi_key", "value", "ts")
    list_filter = ("industry_key", "event_type", "severity")
    search_fields = ("title", "body", "industry_key", "kpi_key")
    ordering = ("-ts",)
