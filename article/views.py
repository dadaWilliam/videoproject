# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
import random
import string
import io
from article.models import Article, FileClass

from asyncio import format_helpers
import base64
from django.http import JsonResponse
from helpers import AuthorRequiredMixin, ajax_required, get_page_list
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import *
from django.views import generic
from ratelimit.decorators import ratelimit
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods

from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db.models import Q
from users.forms import UserLoginForm
from users.models import Token

from videoproject.settings import SITE_URL


User = get_user_model()


class ArticleDetailView(generic.DetailView):
    model = Article
    template_name = 'article/detail.html'

    def get_object(self, queryset=None):
        user_id = self.request.user.id
        user_vip = User.objects.filter(id=user_id).first().vip
        # print('pk')
        # print(self.kwargs.get('pk'))
        id = self.kwargs.get('pk')
        if user_vip:
            obj = get_object_or_404(Article, id=id,)
            # Video.objects.filter(id=id, vip=user_vip)
            # obj = super().get_object()
        else:
            obj = get_object_or_404(Article, id=id, vip=user_vip)
            # Video.objects.filter(id=id)
            # obj = super().get_object()  # .objects.filter(vip=user_vip)
        if obj:
            obj.increase_view_count()
        return obj

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        # form = CommentForm()
        user_id = self.request.user.id
        user_vip = User.objects.filter(id=user_id).first().vip
        if user_vip:
            recommend_list = Article.objects.get_recommend_list()
        else:
            recommend_list = Article.objects.filter(
                vip=user_vip).get_recommend_list()
        # context['form'] = form
        context['recommend_list'] = recommend_list
        return context


def file(request):
    form = UserLoginForm()
    if request.user.id:
        user_vip = User.objects.filter(id=request.user.id).first().vip
        if user_vip:
            files = FileClass.objects.all().filter(status=0)
        else:
            files = FileClass.objects.all().filter(status=0, vip=user_vip)
    else:
        key_tk: str = request.GET.get('tk', '')
        files = FileClass.objects.none()
        if key_tk:
            user = User.objects.filter(token__token=key_tk).first()
            # print(user)
            if user:
                if user.expire:
                    if datetime.now() - user.expire >= timedelta(days=0):
                        messages.warning(request, "用户已失效，请联系管理员")
                        # return HttpResponse("用户已失效，请联系管理员")
                        return render(request, 'registration/login.html', {'form': form, 'next': next, })
                    else:
                        auth_login(request, user)
                        # session_key = request.session.session_key  # 单一设备登陆
                        # for session in Session.objects.filter(~Q(session_key=session_key), expire_date__gte=timezone.now()):
                        #     data = session.get_decoded()
                        #     if data.get('_auth_user_id', None) == str(request.user.id):
                        #         session.delete()
                        # return redirect('home')
                        # return redirect(next)
                else:
                    auth_login(request, user)
                    # session_key = request.session.session_key  # 单一设备登陆
                    # for session in Session.objects.filter(~Q(session_key=session_key), expire_date__gte=timezone.now()):
                    #     data = session.get_decoded()
                    #     if data.get('_auth_user_id', None) == str(request.user.id):
                    #         session.delete()
                    # return redirect('home')
                    # return redirect(next)
                if user.vip:
                    files = FileClass.objects.all().filter(status=0)
                else:
                    files = FileClass.objects.all().filter(status=0, vip=user.vip)
    # user_vip = User.objects.filter(id=request.user.id).first().vip
    # if user_vip:
    #     files = FileClass.objects.all().filter(status=0)
    # else:
    #     files = FileClass.objects.all().filter(status=0, vip=user_vip)
    # file = None
    # desc = None
    # time = None
    # if files:
    #     desc = files.values('desc')
    #     file = files.values('file')
    #     time = files.values('time')
    return render(request, 'file.html', context={'files': files, })


def article(request):
    form = UserLoginForm()
    if request.user.id:
        user_vip = User.objects.filter(id=request.user.id).first().vip
        if user_vip:
            articles = Article.objects.all().filter(status=0)
        else:
            articles = Article.objects.all().filter(status=0, vip=user_vip)
    else:
        key_tk: str = request.GET.get('tk', '')
        articles = Article.objects.none()
        if key_tk:
            user = User.objects.filter(token__token=key_tk).first()
            # print(user)
            if user:
                if user.expire:
                    if datetime.now() - user.expire >= timedelta(days=0):
                        messages.warning(request, "用户已失效，请联系管理员")
                        # return HttpResponse("用户已失效，请联系管理员")
                        return render(request, 'registration/login.html', {'form': form, 'next': next, })
                    else:
                        auth_login(request, user)
                        # session_key = request.session.session_key  # 单一设备登陆
                        # for session in Session.objects.filter(~Q(session_key=session_key), expire_date__gte=timezone.now()):
                        #     data = session.get_decoded()
                        #     if data.get('_auth_user_id', None) == str(request.user.id):
                        #         session.delete()
                        # return redirect('home')
                        # return redirect(next)
                else:
                    auth_login(request, user)
                    # session_key = request.session.session_key  # 单一设备登陆
                    # for session in Session.objects.filter(~Q(session_key=session_key), expire_date__gte=timezone.now()):
                    #     data = session.get_decoded()
                    #     if data.get('_auth_user_id', None) == str(request.user.id):
                    #         session.delete()
                    # return redirect('home')
                    # return redirect(next)
                if user.vip:
                    articles = Article.objects.all().filter(status=0)
                else:
                    articles = Article.objects.all().filter(status=0, vip=user.vip)

    # file = None
    # desc = None
    # time = None
    # if files:
    #     desc = files.values('desc')
    #     file = files.values('file')
    #     time = files.values('time')
    return render(request, './article/article_list.html', context={'articles': articles, })
