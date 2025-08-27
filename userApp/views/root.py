from django.shortcuts import render, redirect
from django.contrib import messages
from userApp.models import *

def index(request):
    title = {
        'title': 'Index',
        'header': 'Header'
    }
    context = {
        'title': title,
    }
    return render(request, 'index.html', context)