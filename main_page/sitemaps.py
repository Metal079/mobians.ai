from datetime import date
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'
    # Update this date whenever the content changes
    lastmod_fixed = date(2023, 4, 11)

    def items(self):
        return ['main_page:index']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return self.lastmod_fixed
