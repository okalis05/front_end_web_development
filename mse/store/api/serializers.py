from rest_framework import serializers
from ..models import Organization, Plan, Subscription, OrgMembership

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["code", "name", "description", "monthly_price_usd", "seats_included", "api_access", "priority_support"]

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "slug", "created_at"]

class MembershipSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = OrgMembership
        fields = ["user", "role", "is_active", "joined_at"]

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    class Meta:
        model = Subscription
        fields = ["plan", "status", "current_period_start", "current_period_end", "cancel_at_period_end"]
