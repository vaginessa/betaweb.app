from django.contrib.sitemaps import Sitemap
from django.conf import settings
from .models import Page
from django.urls import reverse


class PageSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5
    protocol = "http" if settings.DEBUG else "https"

    def items(self):
        return Page.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = 'yearly'

    def items(self):
        return ['dp_downloader_index', 'stories_downloader_index', 'reels_downloader_index',"photo_video_downloader_index","who_unfollowed_index"]

    def location(self, item):
        return reverse(f"app_webapp:{item}")


sitemaps = {
    "page": PageSitemap,
    "static": StaticSitemap
}
