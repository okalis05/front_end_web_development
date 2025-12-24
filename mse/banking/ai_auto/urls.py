from django.urls import path
from . import views

urlpatterns = [
    path("", views.ai_auto_home, name="ai_auto"),
    path("shortlist/", views.ai_auto_shortlist, name="ai_auto_shortlist"),

    path("buyer-plan/", views.buyer_plan, name="ai_auto_buyer_plan"),
    path("buyer-plan/export.pdf", views.buyer_plan_export_pdf, name="ai_auto_buyer_plan_pdf"),

    path("api/message/", views.ai_auto_message_api, name="ai_auto_message_api"),
    path("api/recommend/", views.ai_auto_recommend_api, name="ai_auto_recommend_api"),
    path("buyer-plan/api/add-vehicle/", views.add_vehicle_to_plan_api , name="ai_auto_add_vehicle"
),

    path("inventory/makes/", views.inventory_makes, name="ai_auto_inventory_makes"),
    path("inventory/models/", views.inventory_models, name="ai_auto_inventory_models"),
    path("inventory/trims/", views.inventory_trims, name="ai_auto_inventory_trims"),
]
