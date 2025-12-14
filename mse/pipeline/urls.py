# Dependencies
from django.urls import path
from . import views

# Encapsulating app variables into an umbrella name
app_name = "pipeline"

# Defining pathways to different views
urlpatterns = [
    path("index",views.index , name="index"),
    path("tasks",views.tasks , name="tasks"),
    path("add", views.add , name="add")
]