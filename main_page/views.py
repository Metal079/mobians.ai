import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.templatetags.static import static

# Create your views here.
def index(resquest):
    return render(resquest, 'main_page/index.html')


@csrf_exempt
def process_json(request):
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