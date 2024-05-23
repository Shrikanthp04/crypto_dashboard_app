from django.shortcuts import render
from . import live_plots, nlp_plots 


def home(request):
    return render(request, 'home.html')

def live_plots(request):
    return render(request, 'live_plots.html')

def nlp_plots(request):
    return render(request, 'nlp_plots.html')