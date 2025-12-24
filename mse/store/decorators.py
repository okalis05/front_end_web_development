from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .permissions import require_org, has_role, ROLE_ADMIN_SET, ROLE_ANALYST_SET

def tenant_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not require_org(request):
            messages.info(request, "Select an organization to continue.")
            return redirect("store:org_switch")
        return view_func(request, *args, **kwargs)
    return _wrapped

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not require_org(request) or not has_role(request, ROLE_ADMIN_SET):
            messages.error(request, "Admin privileges required.")
            return redirect("store:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped

def analyst_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not require_org(request) or not has_role(request, ROLE_ANALYST_SET):
            messages.error(request, "Analyst privileges required.")
            return redirect("store:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped
