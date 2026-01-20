from django.urls import path
from . import views

app_name = "powerbi_viz"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("executive/", views.executive_overview, name="executive_overview"),
    path("player/", views.player_impact, name="player_impact"),
    path("health/", views.health_risk, name="health_risk"),
    path("revenue/", views.revenue_fans, name="revenue_fans"),
]
