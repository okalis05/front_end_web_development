# analytics/urls.py
from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [

    path("", views.playground , name="playground"),
    path("landing/", views.landing, name="landing"),
    path("tableau/", views.tableau_gateway, name="tableau"),
    path("index",views.index , name="index")
]


