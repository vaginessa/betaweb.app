from .models import Config, Page
from django.conf import settings


def ConfigContext(request):
    config = Config.objects.values().first() or {}
    pages = Page.objects.values("slug", "title")
    if config:
        for key in config:
            if key in ("favicon_32x32", "favicon_16x16", "favicon_apple", "share_image"):
                config[key] = f"{settings.MEDIA_URL}{config[key]}"
    config["pages"] = pages
    return config
