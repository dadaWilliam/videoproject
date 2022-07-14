from django.urls import path
from . import views

app_name = 'notice'

urlpatterns = [
    # 通知列表
    path('list/', views.NoticeListView.as_view(), name='list'),
    # 更新通知状态
    path('update/', views.NoticeUpdateView.as_view(), name='update'),
]