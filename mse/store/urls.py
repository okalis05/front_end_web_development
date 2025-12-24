from django.urls import path
from .views import (
    StoreLoginView, signup,
    org_switch, org_create,
    dashboard, pricing,
    catalog, product_detail,
    cart, cart_add,
    checkout, billing,
    invoices, audit_log,
)

app_name = "store"

urlpatterns = [
    path("login/", StoreLoginView.as_view(), name="login"),
    path("signup/", signup, name="signup"),

    path("org/", org_switch, name="org_switch"),
    path("org/create/", org_create, name="org_create"),

    path("", dashboard, name="dashboard"),
    path("pricing/", pricing, name="pricing"),
    path("catalog/", catalog, name="catalog"),
    path("product/<slug:slug>/", product_detail, name="product_detail"),

    path("cart/", cart, name="cart"),
    path("cart/add/<int:product_id>/", cart_add, name="cart_add"),

    path("checkout/", checkout, name="checkout"),
    path("billing/", billing, name="billing"),
    path("invoices/", invoices, name="invoices"),
    path("audit/", audit_log, name="audit"),
]
