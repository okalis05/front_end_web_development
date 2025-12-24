from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, OrderViewSet, LedgerViewSet, AuditViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="store-products")
router.register("orders", OrderViewSet, basename="store-orders")
router.register("ledger", LedgerViewSet, basename="store-ledger")
router.register("audit", AuditViewSet, basename="store-audit")

urlpatterns = [
    path("", include(router.urls)),
]
