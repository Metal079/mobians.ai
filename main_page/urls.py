# urls.py
from django.urls import path
from . import views

app_name = 'main_page'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_image/', views.generate_image, name='generate_image'),
    path('retrieve_job/', views.retrieve_job, name='retrieve_job'),
    path('img2img/', views.img2img, name='img2img'),
    path('inpainting/', views.inpainting, name='inpainting'),

]
