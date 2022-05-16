from django.views.generic import TemplateView
from django.shortcuts import render
from .models import User, FollowerRelation, UnfollowerRelation
from .instaPrivate.instagram import insta
from django.db import IntegrityError, transaction
from django.db.models import Q
from .utils.utils import (
    get_or_create_post_by_shortcode,
    get_or_create_user,
    get_or_create_story,
    get_or_create_post_by_shortcode,
    get_or_create_user_posts,
    extractInstaID,
    get_or_create_highlight,
)
insta.login()


class HomeView(TemplateView):
    template_name = "webapp/index.html"


class DPDownloaderView(TemplateView):
    template_name = "webapp/dp-downloader.html"

    def post(self, request):
        username = request.POST.get("username")
        user = get_or_create_user(username=username)
        return render(request, "webapp/profile.html", {"instauser": user})


class StoriesDownloaderView(TemplateView):
    template_name = "webapp/stories-downloader.html"

    def post(self, request):
        username = request.POST.get("username")
        user, stories = get_or_create_story(username=username)
        highlights = get_or_create_highlight(username=username)
        return render(request, "webapp/story.html", {"stories": stories, "instauser": user, "highlights": highlights})


class ReelDetailView(TemplateView):
    template_name = "webapp/reel.html"

    def get(self, request, **kwargs):
        post = get_or_create_post_by_shortcode(**kwargs)
        if not post:
            return render(request, self.template_name)
        return render(request, self.template_name, {"instauser": post.user, "reel": post})


class ReelsDownloaderView(TemplateView):
    template_name = "webapp/reels-downloader.html"

    def post(self, request):
        post = request.POST
        username = post.get("username")
        shortcode = post.get("shortcode")
        context = {}
        if not username:
            try:
                media_type, shortcode = extractInstaID(shortcode)
                if media_type == "reel":
                    post = get_or_create_post_by_shortcode(shortcode=shortcode)
                    if post:
                        context = {"instauser": post.user, "reel": post}
            except TypeError as e:
                pass
        else:
            user, posts = get_or_create_user_posts(
                username=username,
                only_video=True
            )
            context = {"instauser": user,
                       "reels": posts[:(posts.count()//3)*3]
                       }
        return render(request, "webapp/reel.html", context)


class PhotoVideoDownloaderView(TemplateView):
    template_name = "webapp/photo-video-downloader.html"

    def post(self, request):
        post = request.POST
        shortcode = post.get("shortcode")
        context = {}
        try:
            media_type, shortcode = extractInstaID(shortcode)
            if media_type == "p":
                post = get_or_create_post_by_shortcode(shortcode=shortcode)
                if post:
                    context = {"post": post}
        except TypeError:
            pass
        return render(request, "webapp/story.html", context)


class WhoUnfollowedView(TemplateView):
    template_name = "webapp/who-unfollowed.html"

    def post(self, request):
        username = request.POST.get("username")
        to_person = get_or_create_user(username=username)
        followers = {
            follower.username: follower for follower in insta.get_followers(username)
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
                    from_person, created = User.objects.get_or_create(
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
                from_persons = User.objects.filter(username__in=unfollowers_usernames).order_by(
                    "id").values_list("id", flat=True)
                to_person.unfollower.add(*from_persons)
                FollowerRelation.objects.filter(
                    to_person=to_person,
                    from_person__username__in=unfollowers_usernames
                ).delete()
            unfollowers = to_person.unfollower.values()
            return render(request, self.template_name, {"unfollowers": unfollowers,"instauser":to_person})
