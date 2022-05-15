from django.views.generic import TemplateView
from django.shortcuts import render
from .instaPrivate.instagram import insta
from .utils.utils import (
    get_or_create_post_by_shortcode,
    get_or_create_user,
    get_or_create_story,
    get_or_create_post_by_shortcode,
    get_or_create_user_posts,
    extractInstaID
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
        return render(request, "webapp/story.html", {"stories": stories, "instauser": user})


class ReelDetailView(TemplateView):
    template_name = "webapp/reel.html"

    def get(self, request, **kwargs):
        post = get_or_create_post_by_shortcode(**kwargs)
        if not post:
            return render(request, self.template_name)
        user = post.user
        return render(request, self.template_name, {"instauser": user, "reel": post})


class ReelsDownloaderView(TemplateView):
    template_name = "webapp/reels-downloader.html"

    def post(self, request):
        post = request.POST
        username = post.get("username")
        shortcode = post.get("shortcode")
        if not username:
            shortcode = extractInstaID(shortcode)
            post = get_or_create_post_by_shortcode(shortcode=shortcode)
            if post:
                user = post.user
                return render(request, "webapp/reel.html", {"instauser": user, "reel": post})
        else:
            user, posts = get_or_create_user_posts(
                username=username,
                only_video=True
            )
            return render(request, "webapp/reel.html", {"instauser": user, "reels": posts[:(posts.count()//3)*3]})
        return render(request, "webapp/reel.html")


class PhotoVideoDownloaderView(TemplateView):
    template_name = "webapp/photo-video-downloader.html"


class WhoUnfollowedView(TemplateView):
    template_name = "webapp/who-unfollowed.html"
