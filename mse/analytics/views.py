# analytics/views.py
from django.shortcuts import  render


def playground(request):
    return render(request , "analytics/playground.html")

def landing(request):
    return render(request, "analytics/landing.html")

def tableau_gateway(request):
    return render(request, "analytics/tableau.html")

def index(request):
    return render(request , 'analytics/index.html')