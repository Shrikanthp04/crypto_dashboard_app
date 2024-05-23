from django.urls import path
from . import live_plots,nlp_plots, views


urlpatterns = [
    path('', views.home, name='Home'),
    path('live_trend/', views.live_plots, name='Live_plots'),
    path('nlp_plots/', views.nlp_plots, name='Nlp_plots'),
]