from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from ..middleware import TenantMiddleware
from ..models import Plan, OrgMembership
from ..permissions import HasTenant, IsOrgMember, IsOrgAdmin
from .serializers import PlanSerializer, OrganizationSerializer, MembershipSerializer, SubscriptionSerializer

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True).order_by("monthly_price_usd")
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]

class TenantMeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, HasTenant, IsOrgMember]

    def list(self, request):
        org = TenantMiddleware.get_org(request)
        sub = getattr(org, "subscription", None)
        members = OrgMembership.objects.filter(org=org, is_active=True).select_related("user")

        return Response({
            "org": OrganizationSerializer(org).data,
            "subscription": SubscriptionSerializer(sub).data if sub else None,
            "members": MembershipSerializer(members, many=True).data
        })

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated, HasTenant, IsOrgAdmin])
    def admin_only(self, request):
        return Response({"ok": True, "message": "You are an org admin."})
