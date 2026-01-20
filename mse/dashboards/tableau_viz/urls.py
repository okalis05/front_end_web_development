from django.urls import path
from . import views

app_name = "tableau_viz"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("executive/", views.viz, {"view_key": "executive_overview"}, name="executive_overview"),
    path("readmissions/", views.viz, {"view_key": "readmissions"}, name="readmissions"),
    path("cost-impact/", views.viz, {"view_key": "cost_impact"}, name="cost_impact"),
    path("hospital/", views.viz, {"view_key": "hospital_profile"}, name="hospital_profile"),
    path("hospital/<str:facility_id>/", views.viz, {"view_key": "hospital_profile"}, name="hospital_profile_by_id"),
    path("data-sources/", views.data_sources, name="data_sources"),
]
