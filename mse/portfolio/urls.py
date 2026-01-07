# Dependencies
from django.urls import path
from . import views

# Encapsulating the app variables under one name
app_name = 'portfolio'

# PPathways to our views
urlpatterns = [
    path("", views.home , name="home")
]

