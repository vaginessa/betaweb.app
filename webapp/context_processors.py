from .models import Config


def ConfigContext(request):
    config = Config.objects.values().first()
    return config or {}
