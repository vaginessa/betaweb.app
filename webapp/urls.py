from django.urls import path,include
from django.views.decorators.cache import cache_page
from . import views 
app_name = "app_webapp"
sub_urlpatterns = [
    path("dp-downloader/",views.DPDownloaderView.as_view(),name="dp_downloader_index"),
    path("stories-downloader/",views.StoriesDownloaderView.as_view(),name="stories_downloader_index"),
    path("reels-downloader/",views.ReelsDownloaderView.as_view(),name="reels_downloader_index"),
    path("photos-videos-downloader/",views.PhotoVideoDownloaderView.as_view(),name="photo_video_downloader_index"),
    path("who-unfollowed-me-on-instagram/",views.WhoUnfollowedView.as_view(),name="who_unfollowed_index"),
]
urlpatterns = [
    path("",views.HomeView.as_view(),name="home"),
    path("contact/",views.ContactView.as_view(),name="contact"),
    path("instatools/",include(sub_urlpatterns),)
]
