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
from PIL import Image, PngImagePlugin

from dotenv import load_dotenv
load_dotenv()

API_IP = os.environ.get('API_IP')

# Create your views here.
def index(resquest):
    return render(resquest, 'main_page/index.html')


@csrf_exempt
def process_json(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        response = requests.post(url=f'{API_IP}/api/generate/txt2img', json=data)
        r = response.json()

        # Process the data here
        base64_images = []
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
            img_io = io.BytesIO()

            image.save(img_io, "PNG")
            img_io.seek(0)
            base64_images.append(base64.b64encode(img_io.getvalue()).decode('utf-8'))

        return JsonResponse({'images': base64_images})
    else:
        return JsonResponse({'error': 'Invalid request method'})

