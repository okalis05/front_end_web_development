from django.urls import path , include
from django.conf import settings
from . import views
from . import views_ai

app_name = "banking"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("accounts/", views.accounts, name="accounts"),
    path("accounts/<str:public_id>/", views.account_detail, name="account_detail"),
    path("accounts/<str:public_id>/export.csv", views.export_transactions_csv, name="export_csv"),
    path("transfer/", views.transfer, name="transfer"),
    path("billpay/", views.billpay, name="billpay"),
    path("cards/", views.cards, name="cards"),
    path("settings/", views.quick_cash, name="quick_cash"),
    path("scheduled/", views.scheduled_payments, name="scheduled"),
    path("statements/", views.statements, name="statements"),
    path("cards/activity/", views.card_activity, name="card_activity"),
    path("spending/", views.spending, name="spending"),
    path("ai-auto/", include("banking.ai_auto.urls")),
    path("ai-credit/", include("banking.ai_credit.urls")),
    path("ai-portfolio/", views_ai.ai_portfolio_dashboard, name="ai_portfolio"),



]
