from django.shortcuts import render


def intro(request):
    return render(request, "playground/intro.html")


def map_view(request):
    return render(request, "playground/map.html")


def port_insights(request):
    return render(request, "playground/ports.html")


def ai_insights(request):
    return render(request, "playground/insights.html")


def extra(request):
    return render(request , "playground/extra.html")