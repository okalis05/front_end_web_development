from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet, TenantMeViewSet

router = DefaultRouter()
router.register("plans", PlanViewSet, basename="plans")
router.register("tenant", TenantMeViewSet, basename="tenant")

urlpatterns = [
    path("", include(router.urls)),
]
