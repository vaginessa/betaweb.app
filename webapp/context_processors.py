from .models import Config


def ConfigContext(request):
    return Config.objects.values().first()
