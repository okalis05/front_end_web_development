from __future__ import annotations

from typing import Optional
from .middleware import TenantMiddleware
from .models import Organization


def current_tenant(request) -> dict[str, Optional[Organization]]:
    """
    Makes the current tenant organization available in all templates.

    Usage in templates:
        {{ current_org.name }}
        {{ current_org.slug }}
    """
    ctx = getattr(request, "store_tenant", None)
    org = getattr(ctx, "org", None) if ctx else None

    return {
        "current_org": org,
    }
