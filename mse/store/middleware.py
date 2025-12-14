from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from .models import Organization

TENANT_ATTR = "store_tenant"

@dataclass
class TenantContext:
    org: Optional[Organization] = None
    source: str = ""  # header/subdomain/query/session

def _parse_subdomain(host: str) -> Optional[str]:
    if not host:
        return None
    host = host.split(":")[0]
    parts = host.split(".")
    # tenant.example.com -> ["tenant","example","com"]
    if len(parts) >= 3:
        return parts[0]
    return None

class TenantMiddleware(MiddlewareMixin):
    """
    Resolves current tenant Organization:
    Priority:
      1) X-Tenant header (slug)
      2) ?tenant=slug
      3) subdomain (tenant.example.com)
      4) session "store_tenant"
    """
    def process_request(self, request: HttpRequest):
        ctx = TenantContext()

        slug = request.headers.get("X-Tenant", "").strip()
        if slug:
            ctx.source = "header"
        if not slug:
            slug = (request.GET.get("tenant") or "").strip()
            if slug:
                ctx.source = "query"
        if not slug:
            sub = _parse_subdomain(request.get_host())
            if sub:
                slug = sub
                ctx.source = "subdomain"
        if not slug:
            slug = (request.session.get("store_tenant") or "").strip()
            if slug:
                ctx.source = "session"

        if slug:
            try:
                ctx.org = Organization.objects.get(slug=slug)
            except Organization.DoesNotExist:
                ctx.org = None

        setattr(request, TENANT_ATTR, ctx)

    @staticmethod
    def get_org(request: HttpRequest) -> Optional[Organization]:
        ctx = getattr(request, TENANT_ATTR, None)
        return getattr(ctx, "org", None) if ctx else None
