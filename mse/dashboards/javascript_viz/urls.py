from django.urls import path
from . import views

app_name = "javascript_viz"

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboards/<slug:slug>/", views.dashboard, name="dashboard"),
]
