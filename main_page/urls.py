# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process_json', views.process_json, name='process_json'),
    path('image_test_square', views.image_test_square, name='image_test_square'),
    path('get_position/', views.get_position, name='get_position'),
]