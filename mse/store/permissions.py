from rest_framework.permissions import BasePermission
from .middleware import TenantMiddleware
from .selectors import is_org_admin
from .models import OrgMembership

class HasTenant(BasePermission):
    def has_permission(self, request, view):
        return TenantMiddleware.get_org(request) is not None

class IsOrgMember(BasePermission):
    def has_permission(self, request, view):
        org = TenantMiddleware.get_org(request)
        if not org or not request.user.is_authenticated:
            return False
        return OrgMembership.objects.filter(org=org, user=request.user, is_active=True).exists()

class IsOrgAdmin(BasePermission):
    def has_permission(self, request, view):
        org = TenantMiddleware.get_org(request)
        if not org or not request.user.is_authenticated:
            return False
        return is_org_admin(request.user, org)
