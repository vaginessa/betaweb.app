from django import template
from ..models import ImageBase64
from django.conf import settings
from django.core.validators import URLValidator
from base64 import b64encode
validate_url = URLValidator()
register = template.Library()


@register.filter
def toImage(url):
    validate_url(url)
    b64 = b64encode(url.encode("utf8")).decode("utf8")
    try:
        image = ImageBase64.objects.get(
            base64=b64
        )
    except ImageBase64.DoesNotExist:
        image = ImageBase64.objects.create(url=url)
    return settings.MEDIA_URL+str(image.image)
