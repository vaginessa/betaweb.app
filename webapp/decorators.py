from django.shortcuts import render
from .utils.googleservices import verifyCaptcha


def verifyGcaptcha(func):
    def inner_function(*args, **kwargs):
        request = args[0]
        gcaptcha = request.POST.get("gcaptcha")
        if gcaptcha and verifyCaptcha(gcaptcha):
            return func(*args, **kwargs)
        return render(request, "webapp/bot_detection.html")
    return inner_function
