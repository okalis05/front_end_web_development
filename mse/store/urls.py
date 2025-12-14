from django.urls import path
from .views import (
    landing, pricing, dashboard, org_switch, signup,
    start_checkout, checkout_return, billing, open_portal, settings_page,
    stripe_webhook, StoreLoginView,app_dashboard
)

app_name = "store"

urlpatterns = [
    path("", landing, name="landing"),
    path("pricing/", pricing, name="pricing"),
    path("signup/", signup, name="signup"),
    path("login/", StoreLoginView.as_view(), name="login"),

    path("org/", org_switch, name="org_switch"),
    path("dashboard/", dashboard, name="dashboard"),
    path("billing/", billing, name="billing"),
    path("billing/portal/", open_portal, name="open_portal"),
    path("settings/", settings_page, name="settings"),
    path("app/", app_dashboard , name="app"),
    path("checkout/<str:plan_code>/", start_checkout, name="start_checkout"),
    path("checkout/return/", checkout_return, name="checkout_return"),

    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    

]
