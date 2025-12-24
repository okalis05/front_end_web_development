from __future__ import annotations
from .models import Membership

def require_org(request):
    if not getattr(request, "store_org", None):
        return False
    if not request.user.is_authenticated:
        return False
    if not getattr(request, "store_membership", None):
        return False
    return True

def has_role(request, roles: set[str]) -> bool:
    ms = getattr(request, "store_membership", None)
    return bool(ms and ms.role in roles)

ROLE_ADMIN_SET = {Membership.OWNER, Membership.ADMIN}
ROLE_ANALYST_SET = {Membership.OWNER, Membership.ADMIN, Membership.ANALYST}
