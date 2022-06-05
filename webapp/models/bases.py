from django.db import models
from django.utils import timezone


class BaseMedia(models.Model):
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    url = models.URLField(max_length=2083)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.width} x {self.height}"
