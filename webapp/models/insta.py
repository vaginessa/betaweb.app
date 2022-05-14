from django.db import models
from django.utils import timezone
from .bases import BaseMedia
from pathlib import Path
from urllib.parse import urlparse
import requests
from django.conf import settings
from base64 import b64encode


def downloadImage(url, filename):
    with requests.get(url, stream=True) as r:
        assert r.headers["content-type"].split("/")[0] == "image"
        r.raise_for_status()
        with open(settings.MEDIA_ROOT/filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*2):
                f.write(chunk)
    return filename


class ImageBase64(models.Model):
    url = models.URLField(unique=True, max_length=2200)
    base64 = models.TextField(
        null=True, editable=False, db_index=True, blank=True, unique=True)
    image = models.ImageField(
        upload_to="images", editable=False, null=True, blank=True)
    filename = models.CharField(
        max_length=2200, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        self.base64 = b64encode(self.url.encode("utf8")).decode("utf8")
        self.filename = Path(urlparse(self.url).path).resolve().name
        self.image = downloadImage(
            self.url,
            f'{self._meta.get_field("image").upload_to}/{self.filename}'
        )
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "ImagesB64"


class User(models.Model):
    insta_id = models.CharField(max_length=30, unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True, db_index=True)
    posts_count = models.PositiveIntegerField(blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    profile_pic_url = models.URLField(blank=True, null=True)
    profile_pic_url_hd = models.URLField(blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    fbid = models.CharField(max_length=30, blank=True, null=True, unique=True)
    biography = models.CharField(blank=True, null=True, max_length=200)
    followers = models.PositiveIntegerField(blank=True, null=True)
    following = models.PositiveIntegerField(blank=True, null=True)
    is_business_account = models.BooleanField(default=False)
    is_professional_account = models.BooleanField(default=False)
    category_name = models.CharField(max_length=50, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    connected_fb_page = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def __str__(self):
        return self.username

    def __repr__(self):
        return "User(\
            insta_id='{self.insta_id}',\
            username='{self.username}',\
            total_posts={self.total_posts},\
            full_name='{self.full_name}',\
            profile_pic_url='{self.profile_pic_url}',\
            profile_pic_url_hd='{self.profile_pic_url_hd}',\
            external_url='{self.external_url}',\
            fbid='{self.fbid}',\
            biography='{self.biography}',\
            followers={self.followers},\
            following={self.following},\
            is_business_account={self.is_business_account},\
            is_professional_account={self.is_professional_account},\
            category_name='{self.category_name}',\
            is_private={self.is_private},\
            is_verified={self.is_verified},\
            connected_fb_page='{self.connected_fb_page}',\
            )".format(self=self)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name_plural = "InstaUsers"


class Location(models.Model):
    name = models.CharField(max_length=2200)
    lng = models.DecimalField(
        max_digits=8, decimal_places=6, blank=True, null=True)
    lat = models.DecimalField(
        max_digits=8, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=['lng', 'lat'], name='loc_unique'),
        ]


class Post(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post",
        related_query_name="has_post"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="post",
        related_query_name="has_post",
        null=True, blank=True
    )
    insta_id = models.CharField(max_length=30, db_index=True, unique=True)
    shortcode = models.CharField(max_length=100, unique=True, db_index=True)
    taken_at = models.PositiveIntegerField()
    comments_count = models.PositiveIntegerField()
    likes_count = models.PositiveIntegerField()
    filter_type = models.PositiveSmallIntegerField(default=0)
    media_type = models.PositiveSmallIntegerField(default=1)
    original_width = models.PositiveSmallIntegerField(blank=True, null=True)
    original_height = models.PositiveSmallIntegerField(blank=True, null=True)
    caption_is_edited = models.BooleanField(default=False)
    is_paid_partnership = models.BooleanField(default=False)
    comment_likes_enabled = models.BooleanField(default=False)
    is_unified_video = models.BooleanField(default=False)
    is_post_live = models.BooleanField(default=False, null=True)
    commerciality_status = models.CharField(
        max_length=30,
        default="not_commericial"
    )
    product_type = models.CharField(max_length=100, blank=True, null=True)
    caption = models.CharField(max_length=2200, blank=True, null=True)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def __str__(self):
        return self.shortcode

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name_plural = "posts"


class Story(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="story",
        related_query_name="has_story"
    )
    insta_id = models.CharField(max_length=30, db_index=True, unique=True)
    taken_at = models.PositiveIntegerField()
    expiring_at = models.PositiveIntegerField()
    is_video = models.BooleanField(default=False)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.insta_id

    class Meta:
        ordering = ("-updated_at",)
        verbose_name_plural = "stories"


class Image(BaseMedia):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="image",
        related_query_name="has_image",
        blank=True,
        null=True
    )
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="image",
        related_query_name="has_image",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ("-width", "-updated_at",)
        verbose_name_plural = "Images"


class Video(BaseMedia):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="video",
        related_query_name="has_video",
        blank=True,
        null=True
    )
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="video",
        related_query_name="has_video",
        blank=True,
        null=True
    )
    has_audio = models.BooleanField()
    video_duration = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    view_count = models.IntegerField(
        blank=True, null=True
    )

    class Meta:
        ordering = ("-width", "-updated_at",)
        verbose_name_plural = "Videos"


class Highlight(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="highlist",
        related_query_name="has_highlight"
    )
    insta_id = models.CharField(max_length=30, db_index=True, unique=True)
    thumbnail_url = models.URLField()
    cropped_thumbnail_url = models.URLField()
    title = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.insta_id
