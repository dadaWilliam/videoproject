from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from video.models import Video
from notifications.models import Notification
from helpers import get_page_list

class NoticeListView(LoginRequiredMixin, ListView):
    """通知列表"""

    # 上下文的名称
    context_object_name = 'notices'
    # 模板位置
    template_name = 'notice/list.html'
    # 登录重定向
    login_url = '/users/login/'

    model = Notification
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        # classification_list = Classification.objects.filter(status=True).values()
        # context['c'] = self.c
        # context['classification_list'] = classification_list
        context['page_list'] = page_list
        return context

    # 未读+已读通知的查询集
    def get_queryset(self):
        return self.request.user.notifications.unread() | self.request.user.notifications.read()


class NoticeUpdateView(View):
    """更新通知状态"""
    # 处理 get 请求
    def get(self, request):
        # 获取未读消息
        notice_id = request.GET.get('notice_id')
        # 更新单条通知
        if notice_id:
            video_id = request.GET.get('video_id')
            video = Video.objects.get(id=video_id)
            request.user.notifications.get(id=notice_id).mark_as_read()
            video_url = '/video/detail/'+str(video_id)
            return redirect(video_url)
        # 更新全部通知
        else:
            request.user.notifications.mark_all_as_read()
            return redirect('notice:list')