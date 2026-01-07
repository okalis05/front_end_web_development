from django.urls import path
from sentinel import views

app_name = "sentinel"

urlpatterns = [
   
    path("", views.portal, name="portal"),
    path("<str:industry_key>/", views.industry_home, name="industry_home"),
    path("api/industries/", views.api_industries, name="api_industries"),
    path("api/<str:industry_key>/metrics/", views.api_metrics, name="api_metrics"),
    path("api/<str:industry_key>/events/", views.api_events, name="api_events"),
]
