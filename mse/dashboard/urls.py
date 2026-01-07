from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("executive/", views.executive_overview, name="executive_overview"),
    path("readmissions/", views.readmissions, name="readmissions"),
    path("cost-impact/", views.cost_impact, name="cost_impact"),
    path("hospital/<str:facility_id>/", views.hospital_profile, name="hospital_profile"),
    path("data/", views.data_sources, name="data_sources"),
]
