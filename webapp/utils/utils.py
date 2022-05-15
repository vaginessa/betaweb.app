from ..models import User as InstaUser, Story, Image, Video, Post, Location, ScrapingRecord, Highlight
from ..instaPrivate.bases.exceptions import PrivateAccountException, StoriesNotFound, PostNotFound, HighlightNotFound
from ..instaPrivate.instagram import insta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.db.models import Q
import time
import re


def extractInstaID(url):
    mo = re.search(
        r"^https?://[\w\-]*\.?instagram.com\/((?P<type>[\w\._]+)\/(?P<shortcode>[\w\_\-]+)|(?P<username>[\w\.\_]+))\/?$",
        url,
        re.IGNORECASE
    )
    if not mo:
        return
    shortcode = mo.group("shortcode")
    if shortcode:
        media_type = mo.group("type")
        return media_type, shortcode
    return mo.group("username")


def get_create_scraping_record(code):
    return ScrapingRecord.objects.get_or_create(code=code)


def update_scraping_record(instance):
    "need to make it more efficient fails race condition"
    instance.scraped_at = timezone.now()
    instance.save()
    return instance


def get_or_create_user(**kwargs):
    username = kwargs["username"]
    try:
        user = InstaUser.objects.get(username=username)
    except InstaUser.DoesNotExist:
        user_info = insta.get_user_info(username)
        user = InstaUser.objects.create(
            insta_id=user_info.id,
            username=user_info.username,
            posts_count=user_info.posts,
            full_name=user_info.full_name,
            profile_pic_url=user_info.profile_pic_url,
            profile_pic_url_hd=user_info.profile_pic_url_hd,
            external_url=user_info.external_url,
            fbid=user_info.fbid,
            biography=user_info.biography,
            followers=user_info.followers,
            following=user_info.follows,
            is_business_account=user_info.is_business_account,
            category_name=user_info.category_name,
            is_private=user_info.is_private,
            is_verified=user_info.is_verified,
            connected_fb_page=user_info.connected_fb_page
        )
    return user


def get_or_create_story(**kwargs):
    username = kwargs["username"]
    user = get_or_create_user(username=username)
    scrap_code = f"{username}_stories_all"
    scraped_record, created = get_create_scraping_record(scrap_code)
    if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) > (60*60*12):
        try:
            if not created:
                update_scraping_record(scraped_record)
            insta_stories = insta.get_stories(username=username).stories
            for insta_storie in insta_stories:
                with transaction.atomic():
                    try:
                        story = Story.objects.create(
                            user=user,
                            insta_id=insta_storie.id,
                            taken_at=insta_storie.taken_at,
                            expiring_at=insta_storie.expiring_at,
                            is_video=insta_storie.is_video
                        )
                        for image in insta_storie.images:
                            Image.objects.create(
                                width=image.width,
                                height=image.height,
                                url=image.url,
                                story=story
                            )
                        if insta_storie.is_video:
                            for video in insta_storie.videos:
                                Video.objects.create(
                                    story=story,
                                    width=video.width,
                                    height=video.height,
                                    url=video.url,
                                    has_audio=video.has_audio,
                                    video_duration=video.video_duration,
                                    view_count=video.view_count
                                )
                    except IntegrityError as e:
                        # ignores unique contraint error
                        pass
        except StoriesNotFound:
            pass
        except PrivateAccountException:
            pass
    stories = user.story.filter(expiring_at__gte=time.time())
    return user, stories


def get_or_create_location(location_obj):
    if not location_obj:
        return
    try:
        loc = Location.objects.get(
            lng=location_obj.lng, lat=location_obj.lat)
    except Location.DoesNotExist:
        loc = Location.objects.create(
            name=location_obj.name,
            lng=location_obj.lng,
            lat=location_obj.lat
        )
    return loc


def create_post(post_info, user):
    try:
        loc = get_or_create_location(post_info.location)
        post = Post.objects.create(
            user=user,
            location=loc,
            insta_id=post_info.id,
            shortcode=post_info.shortcode,
            taken_at=post_info.taken_at,
            comments_count=post_info.comments,
            likes_count=post_info.likes,
            filter_type=post_info.filter_type,
            media_type=post_info.media_type,
            original_width=post_info.original_width,
            original_height=post_info.original_height,
            caption_is_edited=post_info.caption_is_edited,
            is_paid_partnership=post_info.is_paid_partnership,
            comment_likes_enabled=post_info.comment_likes_enabled,
            is_unified_video=post_info.is_unified_video,
            is_post_live=post_info.is_post_live,
            commerciality_status=post_info.commerciality_status,
            product_type=post_info.product_type,
            caption=post_info.caption,
        )
        for image in post_info.images:
            Image.objects.create(
                width=image.width,
                height=image.height,
                url=image.url,
                post=post
            )
        if post_info.is_unified_video or post_info.media_type == 2:
            for video in post_info.videos:
                Video.objects.create(
                    post=post,
                    width=video.width,
                    height=video.height,
                    url=video.url,
                    has_audio=video.has_audio,
                    video_duration=video.video_duration,
                    view_count=video.view_count
                )
        return post
    except IntegrityError as e:
        return


def get_or_create_user_posts(**kwargs):
    username = kwargs.get("username")
    scrap_code = f"{username}_posts_all"
    user = get_or_create_user(username=username)
    scraped_record, created = get_create_scraping_record(scrap_code)
    if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) >= (60*60*24):
        with transaction.atomic():
            if not created:
                update_scraping_record(scraped_record)
            posts = insta.get_posts(username=username)["posts"]
            for post in posts:
                create_post(post, user)
    if kwargs.get("only_video") == True:
        posts = user.post.filter(Q(media_type=2) | Q(is_unified_video=True))
    else:
        posts = user.post.all()
    return user, posts


def get_or_create_post_by_shortcode(**kwargs):
    shortcode = kwargs.get("shortcode")
    scrap_code = f"{shortcode}_reel_detail"
    with transaction.atomic():
        try:
            post = Post.objects.get(shortcode=shortcode)
        except Post.DoesNotExist:
            scraped_record, created = get_create_scraping_record(scrap_code)
            if not (created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) > (60*60*24)):
                return
            if not created:
                update_scraping_record(scraped_record)
            try:
                post_info = insta.get_post_info(shortcode)
            except PostNotFound:
                return
            user_info = post_info.user
            user = get_or_create_user(username=user_info.username)
            post = create_post(post_info, user)
        return post


def create_highlight(highlight_info, user):
    try:
        return Highlight.objects.create(
            user=user,
            insta_id=highlight_info.id,
            thumbnail_url=highlight_info.thumbnail_url,
            cropped_thumbnail_url=highlight_info.cropped_thumbnail_url,
            title=highlight_info.title,
        )
    except IntegrityError as e:
        return


def get_or_create_highlight(**kwargs):
    username = kwargs["username"]
    scrap_code = f"{username}_highlights_all"
    user = get_or_create_user(username=username)
    scraped_record, created = get_create_scraping_record(scrap_code)
    with transaction.atomic():
        if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) >= (60*60*24):
            if not created:
                update_scraping_record(scraped_record)
            try:
                highlights = insta.get_highlights(username=username)
                for highlight in highlights:
                    create_highlight(highlight,user)
            except HighlightNotFound:
                return 
            except PrivateAccountException:
                return 
    return user.highlight.all()