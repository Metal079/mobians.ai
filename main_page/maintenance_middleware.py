from django.http import HttpResponse
from django.template import loader

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.maintenance_mode = True

    def __call__(self, request):
        if self.maintenance_mode:
            template = loader.get_template('maintenance.html')
            return HttpResponse(template.render(), content_type='text/html')
        return self.get_response(request)
