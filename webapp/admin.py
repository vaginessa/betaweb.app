from django.contrib import admin
from .models import (
    User, Location, Post,
    Story, Image, Video,
    Highlight,ImageBase64,ScrapingRecord
)
admin.site.register([User, Location, Post, Story, Image, Video, Highlight,ImageBase64,ScrapingRecord])
