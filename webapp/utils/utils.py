from ..models import User as InstaUser, CarouselMedia, Story, \
    Image, Video, Post, Location, ScrapingRecord, Highlight, FollowerRelation, UnfollowerRelation, update_user
from webapp.instaPrivate.bases.exceptions import PrivateAccountException, StoriesNotFound, PostNotFound, HighlightNotFound, UserNotFound, F2KException
from webapp.instaPrivate.instagram import insta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.db.models import Q
import time
import re


def isinstaurl(url):
    mo = re.search(r"^https?://[\w\-]*\.?instagram.com", url, re.IGNORECASE)
    return True if mo else False


def getUsername(username):
    if isinstaurl(username):
        parsed = extractInstaID(username)
        if isinstance(parsed, tuple):
            raise UserNotFound
        else:
            username = parsed
    return username


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
    return ScrapingRecord.objects.get_or_create(code=code.lower())


def update_scraping_record(instance):
    "need to make it more efficient fails race condition"
    instance.scraped_at = timezone.now()
    instance.save()
    return instance


def get_or_create_user(**kwargs):
    username = kwargs["username"].lower()
    try:
        user = InstaUser.objects.get(username=username)
        if ((timezone.now() - user.updated_at).total_seconds()) > (60*60*24):
            update_user(user)
    except InstaUser.DoesNotExist:
        scrap_code = f"{username}"
        scraped_record, created = get_create_scraping_record(scrap_code)
        if not created:
            update_scraping_record(scraped_record)
        if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) > (60*60*24):
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
        else:
            raise UserNotFound
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
            insta_stories = insta.get_stories(user_id=user.insta_id).stories
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
                        images = []
                        for image in insta_storie.images:
                            images.append(Image(
                                width=image.width,
                                height=image.height,
                                url=image.url,
                                story=story
                            ))
                        Image.objects.bulk_create(images)
                        if insta_storie.is_video:
                            videos = []
                            for video in insta_storie.videos:
                                videos.append(Video(
                                    story=story,
                                    width=video.width,
                                    height=video.height,
                                    url=video.url,
                                    has_audio=video.has_audio,
                                    video_duration=video.video_duration,
                                    view_count=video.view_count
                                ))
                            Video.objects.bulk_create(videos)
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
        if post_info.media_type == 8:
            images = []
            for cm in post_info.carousel_media:
                cm_ins = CarouselMedia.objects.create(
                    insta_id=cm.id,
                    media_type=cm.media_type,
                    original_width=cm.original_width,
                    original_height=cm.original_height,
                    post=post
                )
                for image in cm.images:
                    images.append(Image(
                        width=image.width,
                        height=image.height,
                        url=image.url,
                        cm=cm_ins
                    ))
            Image.objects.bulk_create(images)
        else:
            images = []
            for image in post_info.images:
                images.append(Image(
                    width=image.width,
                    height=image.height,
                    url=image.url,
                    post=post
                ))
            Image.objects.bulk_create(images)
        if post_info.is_unified_video or post_info.media_type == 2:
            videos = []
            for video in post_info.videos:
                videos.append(Video(
                    post=post,
                    width=video.width,
                    height=video.height,
                    url=video.url,
                    has_audio=video.has_audio,
                    video_duration=video.video_duration,
                    view_count=video.view_count
                ))
            Video.objects.bulk_create(videos)
        return post
    except IntegrityError as e:
        return


def get_or_create_user_posts(**kwargs):
    username = kwargs.get("username")
    scrap_code = f"{username}_posts_all"
    user = get_or_create_user(username=username)
    scraped_record, created = get_create_scraping_record(scrap_code)
    if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) >= (60*60*12):
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
            if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) > (60*60*24):
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
    if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) >= (60*60*24):
        if not created:
            update_scraping_record(scraped_record)
        try:
            highlights = insta.get_highlights(username=username)
            for highlight in highlights:
                create_highlight(highlight, user)
        except HighlightNotFound:
            return
        except PrivateAccountException:
            return
    return user.highlight.all()


def who_unfollowed(username):
    username = getUsername(username)
    to_person = get_or_create_user(username=username)
    if to_person.followers and to_person.followers > 2000:
        raise F2KException(to_person.username)
    try:
        if to_person.is_private:  # user may later change account to private after we save it on db
            raise PrivateAccountException
        scrap_code = f"{username}_who_unfollowed"
        scraped_record, created = get_create_scraping_record(scrap_code)
        if created or ((timezone.now() - scraped_record.scraped_at).total_seconds()) >= (60*60*12):
            if not created:
                update_scraping_record(scraped_record)
            followers = {
                follower.username: follower for follower in insta.get_followers(user_id=to_person.insta_id)
            }
            realtime_followers_usernames = set(followers.keys())
            old_followers_usernames = set(
                to_person.follower.values_list("username", flat=True)
            )
            unfollowers_usernames = old_followers_usernames.difference(
                realtime_followers_usernames)
            new_followers_usernames = realtime_followers_usernames.difference(
                old_followers_usernames)
            with transaction.atomic():
                if new_followers_usernames:
                    UnfollowerRelation.objects.filter(
                        to_person=to_person,
                        from_person__username__in=new_followers_usernames
                    ).delete()
                    for follower_username in new_followers_usernames:
                        follower = followers[follower_username]
                        from_person, created = InstaUser.objects.get_or_create(
                            insta_id=follower.id,
                            username=follower.username,
                            defaults={
                                "full_name": follower.full_name,
                                "profile_pic_url": follower.profile_pic_url,
                                "is_private": follower.is_private,
                                "is_verified": follower.is_verified,
                            }
                        )
                        to_person.follower.add(from_person)
                if unfollowers_usernames:
                    from_persons = InstaUser.objects.filter(username__in=unfollowers_usernames)\
                        .order_by("id").values_list("id", flat=True)
                    to_person.unfollower.add(*from_persons)
                    FollowerRelation.objects.filter(
                        to_person=to_person,
                        from_person__username__in=unfollowers_usernames
                    ).delete()
        unfollowers = to_person.unfollower.values()
    except PrivateAccountException:
        unfollowers = []
    return to_person, unfollowers
