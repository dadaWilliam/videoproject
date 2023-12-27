"""  URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.urls import re_path
from article import views as article_views
from history.models import History
from users import consumer
from video import views
from django.views.static import serve
from django.conf.urls.i18n import i18n_patterns

from rest_framework.routers import DefaultRouter
from video import views
from rest_framework.documentation import include_docs_urls

import notifications.urls

router = DefaultRouter()
router.register(r'video-index-show', views.VideoIndexShowViewSet,
                basename='video-index-show')
router.register(r'video-recommend', views.VideoRecommendViewSet,
                basename='video-recommend')
router.register(r'video', views.VideoViewSet, basename='video')

router.register(r'classification', views.ClassificationViewSet,
                basename='classification')
router.register(r'user', views.UserViewSet, basename='user')
router.register(r'video-history', views.HistoryViewSet,
                basename='history',)
router.register(r'article', views.ArticleViewSet, basename='article')
router.register(r'file', views.FileViewSet, basename='file')

# jwt 验证


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('myadmin/', include('myadmin.urls')),
    path('video/', include('video.urls')),
    path('article/', include('article.urls')),

    path('comment/', include('comment.urls')),
    path('history/', include('history.urls')),
    path('maintenance/', views.maintenance, name='maintenance'),
    path('download/', views.download, name='download'),
    path('ad/', views.ad, name='ad'),

    path('file/', article_views.file, name='file'),
    path('', views.IndexView.as_view(), name='home'),  # 默认首页

    path('docs/', include_docs_urls(title='说明文档')),
    path('api/auth/', views.AuthView.as_view(), name='auth'),  # 登录认证
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('api-check/', views.api_check, name='api-check'),
    # drf 注册路由

    path('api/', include(router.urls)),
    path('api/video-like/<int:code>', views.api_like, name='api-like'),
    path('api/video-collect/<int:code>', views.api_collect, name='api-collect'),
    path('api/video-view/<int:code>', views.api_video_view, name='api-view'),
    # path('api/collected-video/<int:user_id>',
    #      views.VideoCollectedViewSet.as_view()),
    # path('api/liked-video/<int:user_id>', views.VideoLikedViewSet.as_view()),
    path('api/liked-video/', views.VideoLikedViewSet.as_view()),
    path('api/collected-video/', views.VideoCollectedViewSet.as_view()),

    path('api/ad/<int:code>', views.api_ad, name='api-ad'),
    path('api/user-delete/', views.api_user_delete, name='api-user-delete'),


    path('api/update-notice/<int:code>', views.api_notice_update),
    path('api/notice/', views.api_notice),
    path('api/notification/<int:code>',
         views.NotificationViewSet.as_view()),
    # notice
    path('notice/', include('notice.urls', namespace='notice')),
    # 通知
    path('inbox/notifications/',
         include(notifications.urls, namespace='notifications')),
    path("top_notify/", include("django_top_notify.urls")),


    re_path('^static/(?P<path>.*)$', serve,
            {"document_root": settings.STATIC_ROOT}),
    re_path('^upload/(?P<path>.*)$', serve,
            {"document_root": settings.MEDIA_ROOT}),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = views.page_not_found

# websocket_urlpatterns = [
#     re_path(r'ws/notifications/$', consumer.NotificationConsumer.as_asgi()),
# ]
