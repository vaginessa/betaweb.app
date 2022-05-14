from django.views.generic import TemplateView, DetailView
from django.shortcuts import render
from .instaPrivate.instagram import insta
from .instaPrivate.bases.exceptions import PrivateAccountException
from .utils.utils import get_or_create_post_by_shortcode, get_or_create_user, get_or_create_story, get_or_create_post_by_shortcode, get_or_create_user_posts
insta.login()


class HomeView(TemplateView):
    template_name = "webapp/index.html"


class DPDownloaderView(TemplateView):
    template_name = "webapp/dp-downloader.html"

    def get(self, request, **kwargs):
        if not kwargs:
            return super().get(request, **kwargs)
        user = get_or_create_user(**kwargs)
        return render(request, "webapp/profile.html", {"instauser": user})


class StoriesDownloaderView(TemplateView):
    template_name = "webapp/stories-downloader.html"

    def get(self, request, **kwargs):
        if not kwargs:
            return super().get(request, **kwargs)
        user, stories = get_or_create_story(**kwargs)
        return render(request, "webapp/story.html", {"stories": stories, "instauser": user})


class ReelDetailView(TemplateView):
    template_name = "webapp/reel.html"

    def get(self, request, **kwargs):
        post = get_or_create_post_by_shortcode(**kwargs)
        user = post.user
        return render(request, self.template_name, {"instauser": user, "reel": post})


class ReelsDownloaderView(TemplateView):
    template_name = "webapp/reels-downloader.html"

    def get(self, request, **kwargs):
        if not kwargs:
            return super().get(request, **kwargs)
        kwargs.update({"only_video": True})
        user, posts = get_or_create_user_posts(**kwargs)
        return render(request, "webapp/reel.html", {"instauser": user, "reels": posts[:(posts.count()//3)*3]})


class PhotoVideoDownloaderView(TemplateView):
    template_name = "webapp/photo-video-downloader.html"


class WhoUnfollowedView(TemplateView):
    template_name = "webapp/who-unfollowed.html"
