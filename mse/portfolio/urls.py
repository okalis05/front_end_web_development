# Dependencies
from django.urls import path
from . import views

# Encapsulating the app variables under one name
app_name = 'portfolio'

# PPathways to our views
urlpatterns = [
    path('portfolio', views.about, name='about'),
    path('skills/', views.skills, name='skills'),
    path('projects/', views.projects, name='projects'),
    path('contacts/', views.contacts, name='contacts'),
    path("contact_submit/", views.contact_submit, name="contact_submit")
]

