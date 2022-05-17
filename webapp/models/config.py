from django.db import models
from django.utils import timezone


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
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Config"
