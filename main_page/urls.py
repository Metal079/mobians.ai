# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process_json', views.process_json, name='process_json'),
]
