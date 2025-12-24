from django.urls import path
from . import views

urlpatterns = [
    path("", views.ai_credit_home, name="ai_credit"),
    path("api/score/", views.score_credit, name="ai_credit_score"),
    path("api/retrain/", views.retrain_credit_model, name="ai_credit_retrain"),
]
