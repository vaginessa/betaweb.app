from django.urls import path,include
from django.views.decorators.cache import cache_page
from . import views 
app_name = "app_webapp"
sub_urlpatterns = [
    # path("reels-downloader/shortcode/<str:shortcode>/",views.ReelDetailView.as_view(),name="reels_downloader_detail"),
    # path("photos-videos-downloader/shortcode/<str:shortcode>/",views.PhotoVideoDetailView.as_view(),name="photo_video_downloader_detail"),
    # path("who-unfollowed-me-on-instagram/<str:username>/",views.WhoUnfollowedView.as_view(),name="who_unfollowed"),
    # path("dp-downloader/<str:username>/",views.DPDownloaderView.as_view(),name="dp_downloader"),
    # path("stories-downloader/<str:username>/",views.StoriesDownloaderView.as_view(),name="stories_downloader"),
    # path("reels-downloader/<str:username>/",views.ReelsDownloaderView.as_view(),name="reels_downloader"),
    # path("photos-videos-downloader/<str:username>/",views.PhotoVideoDownloaderView.as_view(),name="photo_video_downloader"),
    path("dp-downloader/",views.DPDownloaderView.as_view(),name="dp_downloader_index"),
    path("stories-downloader/",views.StoriesDownloaderView.as_view(),name="stories_downloader_index"),
    path("reels-downloader/",views.ReelsDownloaderView.as_view(),name="reels_downloader_index"),
    path("photos-videos-downloader/",views.PhotoVideoDownloaderView.as_view(),name="photo_video_downloader_index"),
    path("who-unfollowed-me-on-instagram/",views.WhoUnfollowedView.as_view(),name="who_unfollowed_index"),
]
urlpatterns = [
    path("",views.HomeView.as_view(),name="home"),
    path("instatools/",include(sub_urlpatterns),)
]
