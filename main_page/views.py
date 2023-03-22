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

# Create your views here.
def index(resquest):
    return render(resquest, 'main_page/index.html')


@csrf_exempt
def process_json(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        response = requests.post(url=f'https://6827-2601-247-c881-48d0-55a7-90bf-d3f2-b2fe.ngrok.io/sdapi/v1/txt2img', json=data)
        r = response.json()
        remove_user_from_queue(request.session.session_key)

        # Process the data here
        base64_images = []
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
            img_io = io.BytesIO()

            png_payload = {"image": "data:image/png;base64," + i}
            response2 = requests.post(url=f'https://6827-2601-247-c881-48d0-55a7-90bf-d3f2-b2fe.ngrok.io/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))

            image.save(img_io, "PNG", pnginfo=pnginfo)
            img_io.seek(0)
            base64_images.append(base64.b64encode(img_io.getvalue()).decode('utf-8'))

        return JsonResponse({'images': base64_images})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
@csrf_exempt
def image_test_square(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Process the data here
        # For example, let's assume you have a key called "image_name" in the JSON data
        image_name = data.get('image_name', 'default_image_name')

        # Construct the image URL using Django's static files
        image_url_1 = static(f'main_page/sonic.png')
        image_url_2 = static(f'main_page/{image_name}.jpg')
        image_url_3 = static(f'main_page/knuckles.png')
        image_url_4 = static(f'main_page/amy.jpg')

        result = {'image_urls': [image_url_1, image_url_2, image_url_3, image_url_4]}
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'Invalid request method'})
    

# Queue for image generation
queue_lock = Lock()
queue = []

def get_position(request):
    global queue
    user_id = request.session.session_key

    with queue_lock:
        if user_id not in queue:
            queue.append(user_id)
        position = queue.index(user_id)

    return JsonResponse({'position': position + 1})  # Position is 0-indexed, so we add 1

# Remember to remove the user from the queue when the image generation is done
def remove_user_from_queue(user_id):
    global queue
    with queue_lock:
        if user_id in queue:
            queue.remove(user_id)
