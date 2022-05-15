from django.views.generic import TemplateView
from django.shortcuts import render
from .instaPrivate.instagram import insta
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
        return render(request, "webapp/story.html", {"stories": stories, "instauser": user,"highlights":highlights})


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
