import os
import json
import io
import base64
import requests
import random

from django.contrib.staticfiles import finders
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont

from dotenv import load_dotenv
load_dotenv()

API_IP_List = os.environ.get('API_IP_List').split(',')

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

def add_watermark(image, watermark_text, opacity):
    # Create watermark image
    watermark = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    font_file_path = finders.find('fonts/Roboto-Medium.ttf')
    font = ImageFont.truetype(font_file_path, 24)
    draw.text((10, 10), watermark_text, font=font, fill=(255, 255, 255, opacity))

    # Overlay watermark on the original image
    image_with_watermark = Image.alpha_composite(image.convert("RGBA"), watermark)
    return image_with_watermark

@csrf_exempt
def txt2img(request):
    data = json.loads(request.body)

    API_IP = chooseAPI('txt2img')

    response = requests.post(url=f'{API_IP}api/generate/txt2img', json=data)
    r = response.json()

    # Process the data here
    base64_images = []
    watermark_text = "Mobians.ai"
    opacity = 128  # Semi-transparent (0-255)

    for i in r['images'][1:]:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[1])))

        # Add watermark
        image_with_watermark = add_watermark(image, watermark_text, opacity)

        img_io = io.BytesIO()

        # Change to PNG to preserve png info
        image_with_watermark.save(img_io, "PNG")
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

    API_IP = chooseAPI('img2img')

    response = requests.post(url=f'{API_IP}api/generate/img2img', json=data)
    r = response.json()

    watermark_text = "Mobians.ai"
    opacity = 128  # Semi-transparent (0-255)

    # Process the data here
    base64_images = []
    for i in r['images'][1:]:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[1])))
        img_io = io.BytesIO()

        # Add watermark
        image_with_watermark = add_watermark(image, watermark_text, opacity)

        # Change to PNG to preserve png info
        image_with_watermark.save(img_io, "PNG")
        img_io.seek(0)
        base64_images.append(base64.b64encode(
            img_io.getvalue()).decode('utf-8'))

    return JsonResponse({'images': base64_images})

@csrf_exempt
def inpainting(request):
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

    API_IP = chooseAPI('inpainting')

    response = requests.post(url=f'{API_IP}api/generate/inpainting', json=data)
    r = response.json()

    # Process the data here
    base64_images = []
    for i in r['images'][1:]:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[1])))
        img_io = io.BytesIO()

        # Change to PNG to preserve png info
        image.save(img_io, "PNG")
        img_io.seek(0)
        base64_images.append(base64.b64encode(
            img_io.getvalue()).decode('utf-8'))

    return JsonResponse({'images': base64_images})


def chooseAPI(generateType):
    current_apis = API_IP_List.copy()

    if (generateType == 'img2img' or generateType == 'inpainting'):
        API_IP = API_IP_List[0]

    else:
        while current_apis:
            API_IP = random.choice(current_apis)
            if isAPIAlive(API_IP):
                break
            else:
                current_apis.remove(API_IP)

        if not current_apis:
            API_IP = None  # or raise an exception, or some error handling

    return API_IP


def isAPIAlive(API_IP):
    try:
        response = requests.get(url=f'{API_IP}api/test/alive')
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False
