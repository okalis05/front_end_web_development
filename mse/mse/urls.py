from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("portfolio.urls")),
    path("analytics/", include("analytics.urls")),
    path("store/", include("store.urls")),
    path("mystics/", include("mystics_site.urls")),
    path("playground/",include("playground.urls")),
    path("pipeline/",include("pipeline.urls")),
    path("banking/",include("banking.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"))
]
