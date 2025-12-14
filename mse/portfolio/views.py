from django.shortcuts import render

# Create your views here.
def about(request):
    return render(request , "portfolio/about.html")

def projects(request):
    return render(request , "portfolio/projects.html")

def skills(request):
    return render(request , "portfolio/skills.html")

def contacts(request):
    return render(request , "portfolio/contacts.html")



