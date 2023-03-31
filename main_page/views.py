import os
import json
import io
import base64
import requests
from threading import Lock


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.templatetags.static import static
from django.conf import settings
from django.urls import reverse
from PIL import Image, PngImagePlugin

from dotenv import load_dotenv
load_dotenv()

API_IP = os.environ.get('API_IP')

# Create your views here.
def index(resquest):
    return render(resquest, 'main_page/index.html')

@csrf_exempt
def txt2img(request):
    data = json.loads(request.body)

    response = requests.post(url=f'{API_IP}/api/generate/txt2img', json=data)
    r = response.json()

    # Process the data here
    base64_images = []
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        img_io = io.BytesIO()

        # Change to PNG to preserve png info
        image.save(img_io, "JPEG", quality=90)
        img_io.seek(0)
        base64_images.append(base64.b64encode(
            img_io.getvalue()).decode('utf-8'))

    return JsonResponse({'images': base64_images})

@csrf_exempt
def img2img(request):
    print("hello img2img!")
    data = json.loads(request.body)

    response = requests.post(url=f'{API_IP}/api/generate/img2img', json=data)
    r = response.json()

    # Process the data here
    base64_images = []
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        img_io = io.BytesIO()

        # Change to PNG to preserve png info
        image.save(img_io, "JPEG", quality=90)
        img_io.seek(0)
        base64_images.append(base64.b64encode(
            img_io.getvalue()).decode('utf-8'))

    return JsonResponse({'images': base64_images})

