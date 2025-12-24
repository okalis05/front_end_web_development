from __future__ import annotations

import threading
from django.conf import settings
from django.http import HttpRequest
from .models import Organization, Membership

_local = threading.local()

def get_current_org():
    return getattr(_local, "org", None)

def set_current_org(org):
    _local.org = org

class TenantMiddleware:
    """
    Row-level multi-tenancy.
    Resolves tenant by:
      1) cookie STORE_TENANT_COOKIE
      2) querystring ?org=slug (and sets cookie)
    """

    @staticmethod
    def _cookie_name() -> str:
        return getattr(settings, "STORE_TENANT_COOKIE", "store_org")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.store_org = None
        request.store_membership = None

        slug = request.GET.get("org") or request.COOKIES.get(self._cookie_name())
        org = None
        if slug:
            org = Organization.objects.filter(slug=slug, is_active=True).first()

        # If authenticated, ensure membership exists for resolved org
        if org and request.user.is_authenticated:
            ms = Membership.objects.filter(user=request.user, org=org, is_active=True).first()
            if not ms:
                org = None  # forbid tenant hijack

        request.store_org = org
        if org and request.user.is_authenticated:
            request.store_membership = Membership.objects.filter(
                user=request.user, org=org, is_active=True
            ).first()

        set_current_org(org)
        response = self.get_response(request)

        # persist tenant selection if came from querystring
        if request.GET.get("org") and org:
            response.set_cookie(self._cookie_name(), org.slug, samesite="Lax")

        return response
