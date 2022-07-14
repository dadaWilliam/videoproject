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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import re_path,url
from video import views
from django.views.static import serve

from rest_framework.routers import DefaultRouter
from video import views
from rest_framework.documentation import include_docs_urls

import notifications.urls

router = DefaultRouter()
router.register(r'video', views.VideoViewSet)
router.register(r'classification', views.ClassificationViewSet)
router.register(r'user', views.UserViewSet)
#jwt 验证
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/',include('users.urls')),
    path('myadmin/', include('myadmin.urls')),
    path('video/',include('video.urls')),
    path('comment/',include('comment.urls')),
    path('history/',include('history.urls')),
    path('', views.IndexView.as_view(), name='home'), # 默认首页

    path('docs/', include_docs_urls(title='说明文档')),
    url(r'api/auth/$', views.AuthView.as_view(), name='auth'),  # 登录认证
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    # drf 注册路由
    path('api/', include(router.urls)),
    # notice
    path('notice/', include('notice.urls', namespace='notice')),
    # 通知
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path("top_notify/", include("django_top_notify.urls")),

    re_path('^static/(?P<path>.*)$', serve, {"document_root": settings.STATIC_ROOT}),
    re_path('^upload/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = views.page_not_found
