from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Product, Order, LedgerEntry, AuditEvent
from .serializers import (
    ProductSerializer, OrderSerializer, LedgerEntrySerializer, AuditEventSerializer
)

class TenantScopedMixin:
    def get_org(self):
        org = getattr(self.request, "store_org", None)
        if not org:
            return None
        if not self.request.user.is_authenticated:
            return None
        if not getattr(self.request, "store_membership", None):
            return None
        return org

class ProductViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org = self.get_org()
        return Product.objects.none() if not org else Product.objects.filter(org=org, is_active=True).order_by("-created_at")

class OrderViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org = self.get_org()
        return Order.objects.none() if not org else Order.objects.filter(org=org).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def paid(self, request):
        org = self.get_org()
        qs = Order.objects.none() if not org else Order.objects.filter(org=org, status=Order.PAID).order_by("-created_at")
        return Response(OrderSerializer(qs[:50], many=True).data)

class LedgerViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = LedgerEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org = self.get_org()
        return LedgerEntry.objects.none() if not org else LedgerEntry.objects.filter(org=org).order_by("-created_at")

class AuditViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org = self.get_org()
        return AuditEvent.objects.none() if not org else AuditEvent.objects.filter(org=org).order_by("-created_at")
