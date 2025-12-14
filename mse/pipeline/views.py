from django.shortcuts import render
import datetime
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

name = input("What's Your Name?").capitalize()
class NewTaskForm(forms.Form):
    task = forms.CharField(label='Add Task')
# Create your views here.

tasks = []
now = datetime.datetime.now()

def index(request):
    return render(request , "pipeline/index.html",{
        "name": name,
        "time": now

    })

def tasks(request):
    if "tasks" not in request.session:
        request.session['tasks']
    return render(request,'pipeline/tasks.html',{
        'tasks':tasks
    })


def add(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            task = form.cleaned_data['task']
            request.session['tasks'] +=[task]
            return HttpResponseRedirect(reverse('pipeline:tasks'))
        else:
            return render(request , "pipeline/add.html",{
                "form":form
   
    })
    return render(request , 'pipeline/add.html',{

    })