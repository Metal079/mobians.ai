# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('txt2img/', views.txt2img, name='txt2img'),
    path('img2img/', views.img2img, name='img2img'),
    path('inpainting/', views.inpainting, name='inpainting'),
]
