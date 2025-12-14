from django.urls import path
from . import views

app_name = "playground"

urlpatterns = [
    path("", views.intro, name="intro"),
    path("map/", views.map_view, name="map"),
    path("ports/", views.port_insights, name="ports"),
    path("insights/", views.ai_insights, name="insights"),
    path("extra/", views.extra , name="extra")
]
