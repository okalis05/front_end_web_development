
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.shortcuts import redirect


urlpatterns = [
    path("", lambda request: redirect("mystics_site:home")),
    path("admin/", admin.site.urls),
    path("portfolio/", include("portfolio.urls")),
    path("analytics/", include("analytics.urls")),
    path("pipeline/", include("pipeline.urls")),
    path("mystics_site/", include("mystics_site.urls")),
    path("playground/", include("playground.urls")),
    path("banking/", include("banking.urls")),
    path("store/", include("store.urls")),
    path("store/api/", include("store.api_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema")),
]
