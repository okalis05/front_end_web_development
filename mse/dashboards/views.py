from django.shortcuts import render
from django.urls import reverse


# Create your views here.
def landing(request):
    return render(request, "dashboards/landing.html", {"active": "landing"})
