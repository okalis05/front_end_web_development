from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from django.contrib.auth import get_user_model

from .models import Organization, OrgMembership, ROLE_ADMIN

# ─────────────────────────────────────────────
# Typing-safe User reference
# ─────────────────────────────────────────────
if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    UserType = AbstractBaseUser
else:
    UserType = get_user_model()


def get_user_orgs(user: UserType):
    return (
        Organization.objects
        .filter(memberships__user=user, memberships__is_active=True)
        .distinct()
    )


def get_membership(
    user: UserType,
    org: Organization
) -> Optional[OrgMembership]:
    try:
        return OrgMembership.objects.get(
            user=user,
            org=org,
            is_active=True,
        )
    except OrgMembership.DoesNotExist:
        return None


def is_org_admin(user: UserType, org: Organization) -> bool:
    membership = get_membership(user, org)
    return bool(membership and membership.role == ROLE_ADMIN)
