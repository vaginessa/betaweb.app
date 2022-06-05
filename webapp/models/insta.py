from django.db import models
from django.utils import timezone
from .bases import BaseMedia
from pathlib import Path
from urllib.parse import urlparse
from webapp.instaPrivate.instagram import insta
from django.conf import settings
from base64 import b64encode
from PIL import ImageFile


def update_video(parent_instance, video_info):
    try:
        video = parent_instance.video.filter(
            height=video_info.height,
            width=video_info.width
        ).first()
        if video:
            video.url = video_info.url
            video.view_count = video_info.view_count
            video.save()
            return video
    except Video.DoesNotExist:
        pass


def update_post(instance):
    post_info = insta.get_post_info(instance.shortcode)
    instance.comments_count = post_info.comments
    instance.likes_count = post_info.likes
    instance.caption_is_edited = post_info.caption_is_edited
    instance.comment_likes_enabled = post_info.comment_likes_enabled
    instance.caption = post_info.caption
    if post_info.is_unified_video or post_info.media_type == 2:
        for video in post_info.videos:
            update_video(instance, video)
    instance.save()
    return instance


def update_user(instance):
    user_info = insta.get_user_info(instance.username)
    instance.insta_id = user_info.id
    instance.username = user_info.username
    instance.posts_count = user_info.posts
    instance.full_name = user_info.full_name
    instance.profile_pic_url = user_info.profile_pic_url
    instance.profile_pic_url_hd = user_info.profile_pic_url_hd
    instance.external_url = user_info.external_url
    instance.fbid = user_info.fbid
    instance.biography = user_info.biography
    instance.followers = user_info.followers
    instance.following = user_info.follows
    instance.is_business_account = user_info.is_business_account
    instance.category_name = user_info.category_name
    instance.is_private = user_info.is_private
    instance.is_verified = user_info.is_verified
    instance.connected_fb_page = user_info.connected_fb_page
    instance.save()
    return instance


def downloadImage(url, filename):
    filepath = settings.MEDIA_ROOT/filename
    with ImageFile.Parser() as p:
        with insta.session.get(url, stream=True) as r:
            assert r.headers["content-type"].split("/")[0] == "image"
            r.raise_for_status()
            with open(filepath, "wb+") as f:
                for chunk in r.iter_content(chunk_size=1024*2):
                    f.write(chunk)
                f.seek(0)
                p.feed(f.read())
            if p.image:
                width, height = p.image.size
                path = Path(settings.MEDIA_ROOT/filename)
                filename = f"images/{path.stem}{width}x{height}{path.suffix}"
                path.rename(
                    settings.MEDIA_ROOT / filename
                )
    return filename


class ScrapingRecord(models.Model):
    code = models.CharField(max_length=400, unique=True, db_index=True)
    scraped_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code


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


class FollowUnfollowABC(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class FollowerRelation(FollowUnfollowABC):
    to_person = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="follow_to_person")
    from_person = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="follow_from_person")

    def __str__(self):
        return f"{self.from_person} followed {self.to_person}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['to_person', 'from_person'], name='follow_rel_unique'),
        ]


class UnfollowerRelation(FollowUnfollowABC):
    to_person = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="unfollow_to_person")
    from_person = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="unfollow_from_person")

    def __str__(self):
        return f"{self.from_person} unfollowed {self.to_person}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['to_person', 'from_person'], name='unfollow_rel_unique'),
        ]


class User(models.Model):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if ((timezone.now() - self.updated_at).total_seconds()) >= (60*60*24):
    #         update_user(self)
    follower = models.ManyToManyField(
        "self", symmetrical=False, through="FollowerRelation", related_name="follows")
    unfollower = models.ManyToManyField(
        "self", symmetrical=False, through="UnfollowerRelation", related_name="unfollows")
    insta_id = models.CharField(max_length=30, unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True, db_index=True)
    posts_count = models.PositiveIntegerField(blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    profile_pic_url = models.URLField(max_length=2083, blank=True, null=True)
    profile_pic_url_hd = models.URLField(
        max_length=2083, blank=True, null=True)
    external_url = models.URLField(max_length=2083, blank=True, null=True)
    fbid = models.CharField(max_length=30, blank=True, null=True, unique=True)
    biography = models.CharField(blank=True, null=True, max_length=2000)
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (((timezone.now() - self.updated_at).total_seconds()) > (60*60*8)) and (self.is_unified_video or self.media_type == 2):
            update_post(self)
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


class CarouselMedia(models.Model):
    insta_id = models.CharField(max_length=30, db_index=True, unique=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="cm", related_query_name="has_cm")
    media_type = models.PositiveSmallIntegerField(default=1)
    original_width = models.PositiveSmallIntegerField(blank=True, null=True)
    original_height = models.PositiveSmallIntegerField(blank=True, null=True)


class Image(BaseMedia):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="image",
        related_query_name="has_image",
        blank=True,
        null=True
    )
    cm = models.ForeignKey(
        CarouselMedia,
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
        related_name="highlight",
        related_query_name="has_highlight"
    )
    insta_id = models.CharField(max_length=30, db_index=True, unique=True)
    thumbnail_url = models.URLField(max_length=2083)
    cropped_thumbnail_url = models.URLField(max_length=2083)
    title = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.insta_id
# class
