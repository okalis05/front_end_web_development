from django.urls import path , include
from . import views

app_name = "dashboards"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("powerbi/", include("dashboards.powerbi_viz.urls"),name='powerbi'),
    path("tableau/", include("dashboards.tableau_viz.urls"),name='tableau'),
    path("javascript/", include("dashboards.javascript_viz.urls"),name='javascript')
]
