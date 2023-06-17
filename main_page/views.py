import os
import json
import io
import base64
import requests
import random
import time

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
    font = ImageFont.truetype(font_file_path, 25)
    draw.text((10, 10), watermark_text, font=font, fill=(255, 255, 255, opacity))

    # Overlay watermark on the original image
    image_with_watermark = Image.alpha_composite(image.convert("RGBA"), watermark)
    return image_with_watermark

@csrf_exempt
def txt2img(request):
    data = json.loads(request.body)

    data['data']['prompt'], data['data']['negative_prompt'] = promptFilter(data)
    data['data']['negative_prompt'] = fortify_default_negative(data['data']['negative_prompt'])

    API_IP = 'http://76.157.184.213:5003/'

    # Try using the requested API, if it fails, use the other one
    response = requests.post(url=f'{API_IP}api/generate/txt2img', json=data)
    attempts = 0
    while response.status_code != 200 and attempts < 3:
        if response.status_code == 404:
            API_IP = chooseAPI('txt2img', [API_IP])
            print("got 404")
        elif response.status_code == 503:
            time.sleep(3)
            print("got 503")
        else:
            print(f"got other error: {response.status_code}")
            break
        attempts += 1
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

    data['data']['prompt'], data['data']['negative_prompt'] = promptFilter(data)
    data['data']['negative_prompt'] = fortify_default_negative(data['data']['negative_prompt'])

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
    response = requests.post(url=f'{API_IP}api/generate/img2img', json=data, verify=False)
    try:
        r = response.json()
    except:
        API_IP = chooseAPI('img2img', [API_IP])
        response = requests.post(url=f'{API_IP}api/generate/img2img', json=data, verify=False)
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

    data['data']['prompt'], data['data']['negative_prompt'] = promptFilter(data)
    data['data']['negative_prompt'] = fortify_default_negative(data['data']['negative_prompt'])

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
    try:
        r = response.json()
    except:
        API_IP = chooseAPI('inpainting', [API_IP])
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


def chooseAPI(generateType, triedAPIs = []):
    current_apis = API_IP_List.copy()

    if (generateType == 'inpainting'):
        API_IP = API_IP_List[0]

    else:
        if len(triedAPIs) > 0:
            for i in triedAPIs:
                current_apis.remove(i)
        API_IP = random.choice(current_apis)

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

def promptFilter(data):
    prompt = data['data']['prompt']
    negative_prompt = data['data']['negative_prompt']

    character_list = ['cream the rabbit', 
                      'rosy the rascal',
                      'sage',
                      'maria robotnik',
                      'marine the raccoon',
                      'sage']
    
    censored_tags = ['breast',
                     'nipples',
                     'pussy',
                     'nsfw',
                     'nudity',
                     'naked',
                     'loli',
                     'nude',
                     'ass',
                     'rape',
                     'sex',
                     'boob',
                     'sexy',
                     'busty',
                     'tits',
                     'thighs',
                     'thick']

    # If character is in prompt, filter out censored tags from prompt
    if any(character in prompt.lower() for character in character_list):
        for tag in censored_tags:
            prompt = prompt.replace(tag, '')
        negative_prompt = "nipples, pussy, breasts, " + negative_prompt
            
    return prompt, negative_prompt

def fortify_default_negative(negative_prompt):
    if "nsfw" in negative_prompt.lower() and "nipples" not in negative_prompt.lower():
        return "nipples, pussy, breasts, " + negative_prompt
    else:
        return negative_prompt
    