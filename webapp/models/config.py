from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Config(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    disclaimer = models.CharField(max_length=500, null=True, blank=True)
    favicon_32x32 = models.ImageField(
        upload_to="images/defaults", null=True, blank=True)
    favicon_16x16 = models.ImageField(
        upload_to="images/defaults", null=True, blank=True)
    favicon_apple = models.ImageField(
        upload_to="images/defaults", null=True, blank=True)
    share_image = models.ImageField(
        upload_to="images/defaults", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        self.id = 1
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Config"


class Page(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    slug = models.SlugField(editable=False)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-updated_at",)
