from rest_framework import serializers
from .models import Product, Order, OrderItem, LedgerEntry, AuditEvent

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "price", "currency", "accent", "image_url", "is_active", "created_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "qty", "unit_price", "line_total"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ["id", "status", "currency", "subtotal", "tax", "total", "created_at", "items"]

class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = ["id", "direction", "amount", "currency", "memo", "event_code", "created_at"]

class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = ["id", "action", "detail", "created_at"]
