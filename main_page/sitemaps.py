import os
from datetime import date
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['main_page:index']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Replace 'your_app_name' with the name of your Django app
        template_path = os.path.join(
            'main_page', 'templates', 'main_page', 'index.html')
        modification_time = os.path.getmtime(template_path)
        return date.fromtimestamp(modification_time)
