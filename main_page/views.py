import os
import json
import io
import base64
import requests
from threading import Lock


from django.http import JsonResponse, HttpResponse
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

def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Disallow: /*\n"
        "Allow: /$\n"
        "Sitemap: https://mobians.ai/sitemap.xml"
    )
    return HttpResponse(content, content_type="text/plain")

@csrf_exempt
def txt2img(request):
    data = json.loads(request.body)

    response = requests.post(url=f'{API_IP}/api/generate/txt2img', json=data)
    r = response.json()

    # Process the data here
    base64_images = []
    for i in r['images'][1:]:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[1])))
        img_io = io.BytesIO()

        # Change to PNG to preserve png info
        image.save(img_io, "JPEG", quality=90)
        img_io.seek(0)
        base64_images.append(base64.b64encode(
            img_io.getvalue()).decode('utf-8'))

    return JsonResponse({'images': base64_images})

@csrf_exempt
def img2img(request):
    data = json.loads(request.body)

    # Convert base64 string to image to remove alpha channel if needed
    received_image = Image.open(io.BytesIO(base64.b64decode(data['data']['image'].split(",", 1)[0])))
    if received_image.mode == 'RGBA':
        buffer = io.BytesIO()
        
        # Seperate alpha channel and add white background
        background = Image.new('RGBA', received_image.size, (255, 255, 255))
        alpha_composite = Image.alpha_composite(background, received_image).convert('RGB')
        alpha_composite.save(buffer, format='PNG')

        # Convert received_image back to base64 string
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data['data']['image'] = encoded_image

    response = requests.post(url=f'{API_IP}/api/generate/img2img', json=data)
    r = response.json()

    # Process the data here
    base64_images = []
    for i in r['images'][1:]:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[1])))
        img_io = io.BytesIO()

        # Change to PNG to preserve png info
        image.save(img_io, "JPEG", quality=90)
        img_io.seek(0)
        base64_images.append(base64.b64encode(
            img_io.getvalue()).decode('utf-8'))

    return JsonResponse({'images': base64_images})

@csrf_exempt
def inpainting(request):
    data = json.loads(request.body)

    response = requests.post(url=f'{API_IP}/api/generate/inpainting', json=data)
    r = response.json()

    # Process the data here
    base64_images = []
    for i in r['images'][1:]:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[1])))
        img_io = io.BytesIO()

        # Change to PNG to preserve png info
        image.save(img_io, "JPEG", quality=90)
        img_io.seek(0)
        base64_images.append(base64.b64encode(
            img_io.getvalue()).decode('utf-8'))

    return JsonResponse({'images': base64_images})