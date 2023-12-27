from urllib import request
from rest_framework import viewsets, mixins
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib import messages
from article.models import AD

from django_tctip.models import Tip
from video.serializers import *

from helpers import get_page_list, ajax_required
from videoproject import settings
from .forms import CommentForm
from .models import Video, Classification
from history.models import History
from users.models import User, Token, Repair, Software

from video.permissions import IsAdminUserOrReadOnly, IsAuthenticatedAndDeleteOnly
from rest_framework import viewsets, generics
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes

from datetime import datetime, timedelta
from history.mixins import ObjectViewMixin
import json
from django.contrib.contenttypes.models import ContentType


def page_not_found(request, exception):
    return render(request, "404.html",)

# api


class UserViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        # self.kwargs.get
        # self.request.GET.get("tk", None)
        # self.request.user
        # tk = self.request.GET.get("tk", None)
        # # print(self.request.GET.get("tk", None))
        # if tk is not None:
        #     users = User.objects.filter(
        #         token__token=tk)
        #     return users  # no [0]
        # else:
        #     return None
        return User.objects.filter(id=self.request.user.id)


class ClassificationViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    # queryset = Classification.objects.all()
    serializer_class = ClassificationSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        user_vip = User.objects.filter(id=self.request.user.id).first().vip
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        #     user_vip = User.objects.filter(
        #         token__token=tk)[0].vip
        if user_vip:
            classifications = Classification.objects.filter(
                status=True).order_by('-time')
        else:
            classifications = Classification.objects.filter(
                status=True).order_by('-time').filter(vip=user_vip)
        return classifications
        # else:
        #     return None


class VideoViewSet(viewsets.ModelViewSet):
    # queryset = Video.objects.filter(status=0).order_by('-create_time')
    serializer_class = VideoSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        #     user_vip = User.objects.filter(
        #         token__token=tk)[0].vip
        user_vip = User.objects.filter(id=self.request.user.id).first().vip
        if user_vip:
            videos = Video.objects.filter(
                status=0).order_by('-create_time')
        else:
            videos = Video.objects.filter(status=0).order_by(
                '-create_time').filter(vip=user_vip)
        return videos
        # else:
        #     return None

    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'classification__title']


class VideoIndexShowViewSet(viewsets.ModelViewSet):
    # queryset = Video.objects.get_index_show()
    serializer_class = VideoSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        user_vip = User.objects.filter(id=self.request.user.id).first().vip
        # user_vip = User.objects.filter(
        #     token__token=tk)[0].vip
        if user_vip:
            videos = Video.objects.get_index_show()
        else:
            videos = Video.objects.get_index_show().filter(vip=user_vip)
        return videos
        # else:
        #     return None


class VideoCollectedViewSet(generics.ListCreateAPIView):
    serializer_class = VideoSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        user = User.objects.filter(id=self.request.user.id).first()
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        # user = User.objects.filter(
        #     token__token=tk)[0]
        # user = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        # print(self.kwargs.get('video_id'))
        if user.vip:
            videos = user.collected_videos.all()
        else:
            videos = user.collected_videos.all().filter(vip=user.vip)
        return videos
        # else:
        #     return None


class VideoLikedViewSet(generics.ListCreateAPIView):
    serializer_class = VideoSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        user = User.objects.filter(id=self.request.user.id).first()
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        #     user = User.objects.filter(
        #         token__token=tk)[0]
        #     # user = User.objects.filter(token__token=token)
        #     # user = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        #     # print(self.kwargs.get('video_id'))
        if user.vip:
            videos = user.liked_videos.all()

        else:
            videos = user.liked_videos.all().filter(vip=user.vip)
        return videos


class VideoRecommendViewSet(viewsets.ModelViewSet):
    # queryset = Video.objects.get_recommend_list()
    serializer_class = VideoSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        #     user_vip = User.objects.filter(
        #         token__token=tk)[0].vip
        user_vip = User.objects.filter(id=self.request.user.id).first().vip

        if user_vip:
            videos = Video.objects.get_recommend_list()
        else:
            videos = Video.objects.filter(vip=user_vip).get_recommend_list()
        return videos
        # else:
        #     return None


class HistoryViewSet(viewsets.ModelViewSet):

    # queryset = History.objects.all().order_by('-viewed_on')
    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticatedAndDeleteOnly,)
    # permission_classes = [IsAdminUserOrReadOnly]

    # filter_backends = [filters.SearchFilter]
    # # filter_fields = ['user__id','id']
    # search_fields = ['=user__id', ]
    def get_queryset(self):
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        user = User.objects.filter(id=self.request.user.id).first()
        # user = User.objects.filter(
        #     token__token=tk)[0]
        histories = History.objects.filter(
            user=user).order_by('-viewed_on')
        # mind change of VIP  !!! solved in serializer
        # if user_vip:
        #     histo = Video.objects.get_recommend_list()
        # else:
        #     videos = Video.objects.get_recommend_list().filter(vip=user_vip)
        return histories
        # else:
        #     return None


class NotificationViewSet(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        # tk = self.request.GET.get("tk", None)
        # if tk is not None:
        #     user = User.objects.filter(
        #         token__token=tk)[0]
        # get_object_or_404(User, pk=self.kwargs.get('user_id'))
        user = User.objects.filter(id=self.request.user.id).first()
        code = self.kwargs.get('code')
        # print(self.kwargs.get('video_id'))
        if code == 0:
            notifications = Notification.objects.filter(
                recipient=user, unread=True)
        elif code == 1:
            notifications = Notification.objects.filter(
                recipient=user, unread=False)
        else:
            notifications = Notification.objects.filter(recipient=user,)
        return notifications
        # else:
        #     return None

# class NotificationViewSet(viewsets.ModelViewSet):
#     queryset = Notification.objects.all()
#     serializer_class = NotificationSerializer
#     permission_classes = (IsAuthenticated,)
#     # permission_classes = [IsAdminUserOrReadOnly]
#
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['user__id',]

# login token


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        user = User.objects.filter(id=self.request.user.id).first()
        if user:
            if user.vip:
                return FileClass.objects.filter(status=0)
            else:
                return FileClass.objects.filter(status=0, vip=user.vip)
        else:
            return FileClass.objects.none()


class ArticleViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ArticleSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        user = User.objects.filter(id=self.request.user.id).first()
        if user:
            if user.vip:
                return Article.objects.filter(status=0)
            else:
                return Article.objects.filter(status=0, vip=user.vip)
        else:
            return Article.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return super().get_serializer_class()


def generate_token(username):
    """根据用户名和时间，进行MD5值"""
    import time
    import hashlib

    md5 = hashlib.md5(username.encode('utf-8'))
    md5.update(str(time.time()).encode('utf-8'))

    return md5.hexdigest()


class AuthView(APIView):
    def post(self, request, *args, **kwargs):
        res = {'code': 1000,  # code: 1000 登录成功；1001登录失败
               'msg': 'OK',   # 错误信息
               'user': None,
               'create_time': datetime.now(),
               'token': None}

        username = request._request.POST.get('username')
        pwd = request._request.POST.get('pwd')
        # print('username:',username)
        # print('pwd:',pwd)
        user_obj = authenticate(username=username, password=pwd)
        #user_obj = User.objects.filter(username=username, password=pwd).first()
        if user_obj:  # 如果用户存在，那么生成token并更新
            if user_obj.expire is not None:
                if datetime.now() - user_obj.expire >= timedelta(days=0):  # 用户失效
                    res['code'] = 1002
                    res['msg'] = 'User expired'
                else:
                    token = generate_token(username)

                    Token.objects.update_or_create(
                        user=user_obj, defaults={'token': token, })
                    res['user'] = user_obj.id
                    res['token'] = token
            else:  # 永久有效用户
                token = generate_token(username)
                Token.objects.update_or_create(
                    user=user_obj, defaults={'token': token})
                res['user'] = user_obj.id
                res['token'] = token
        else:
            res['code'] = 1001
            res['msg'] = 'Username or Password error'

        return JsonResponse(res)

###


class IndexView(generic.ListView):
    model = Video
    template_name = 'video/index.html'
    context_object_name = 'video_list'
    paginate_by = 12
    c = None

    def get_context_data(self, *, object_list=None, **kwargs):
        user_id = self.request.user.id
        user_vip = User.objects.filter(id=user_id).first().vip

        context = super(IndexView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        if user_vip:
            classification_list = Classification.objects.filter(
                status=True).order_by('-time').values()
        else:
            classification_list = Classification.objects.filter(
                status=True, vip=user_vip).order_by('-time').values()
        context['c'] = self.c
        context['classification_list'] = classification_list
        context['page_list'] = page_list
        return context

    def get_queryset(self):
        user_id = self.request.user.id
        user_vip = User.objects.filter(id=user_id)[0].vip

        self.c = self.request.GET.get("c", None)
        if self.c:
            classification = get_object_or_404(
                Classification, pk=self.c, status=True)
            if user_vip:
                return classification.video_set.all().order_by('-create_time').filter(status=0)
            else:
                return classification.video_set.all().order_by('-create_time').filter(status=0, vip=user_vip)
        # elif self.c:
        #     return Video.objects.none()
        else:
            if user_vip:
                return Video.objects.filter(status=0).order_by('-create_time')
            else:
                return Video.objects.filter(status=0, vip=user_vip).order_by('-create_time')


class SearchListView(generic.ListView):
    model = Video
    template_name = 'video/search.html'
    context_object_name = 'video_list'
    paginate_by = 8
    q = ''

    def get_queryset(self):
        user_id = self.request.user.id
        user_vip = User.objects.filter(id=user_id).first().vip
        self.q = self.request.GET.get("q", "")
        if user_vip:
            return Video.objects.filter(title__contains=self.q).filter(status=0)
        else:
            return Video.objects.filter(title__contains=self.q).filter(status=0, vip=user_vip)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context


class VideoDetailView(ObjectViewMixin, generic.DetailView):
    model = Video
    template_name = 'video/detail.html'

    def get_object(self, queryset=None):
        user_id = self.request.user.id
        user_vip = User.objects.filter(id=user_id).first().vip
        print('pk')
        print(self.kwargs.get('pk'))
        id = self.kwargs.get('pk')
        if user_vip:
            obj = get_object_or_404(Video, id=id,)
            # Video.objects.filter(id=id, vip=user_vip)
            # obj = super().get_object()
        else:
            obj = get_object_or_404(Video, id=id, vip=user_vip)
            # Video.objects.filter(id=id)
            # obj = super().get_object()  # .objects.filter(vip=user_vip)
        if obj:
            obj.increase_view_count()
        return obj

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        user_id = self.request.user.id
        user_vip = User.objects.filter(id=user_id).first().vip
        if user_vip:
            recommend_list = Video.objects.get_recommend_list()
        else:
            recommend_list = Video.objects.filter(
                vip=user_vip).get_recommend_list()
        context['form'] = form
        context['recommend_list'] = recommend_list
        return context


@ajax_required
@require_http_methods(["POST"])
def like(request):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 1, "msg": "请先登录"})
    video_id = request.POST['video_id']
    video = Video.objects.get(pk=video_id)
    user = request.user
    video.switch_like(user)
    return JsonResponse({"code": 0, "likes": video.count_likers(), "user_liked": video.user_liked(user)})


@ajax_required
@require_http_methods(["POST"])
def collect(request):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 1, "msg": "请先登录"})
    video_id = request.POST['video_id']
    video = Video.objects.get(pk=video_id)
    user = request.user
    video.switch_collect(user)
    return JsonResponse({"code": 0, "collects": video.count_collecters(), "user_collected": video.user_collected(user)})


@api_view(['POST', 'GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_like(request, code):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 2002, "msg": "请先登录"})
    else:
        if request.method == "POST":
            # print(request.content_type)
            # Content-type为application/json时 用下面的方法获取数据
            if request.content_type.startswith('application/json'):
                data_json = json.loads(request.body)
                video_id = data_json.get('video_id')
            else:
                video_id = request.POST.get('video_id')
            # print(video_id)
        else:
            video_id = request.query_params.get('video_id')
        if video_id is None:
            # print(video_id)
            return JsonResponse({"code": 2003, })
        else:
            video = Video.objects.get(pk=video_id)
            user = request.user
            if code == 1:
                video.switch_like(user)
                # 用户喜欢
                return JsonResponse({"code": 2001, "likes": video.count_likers(), "user_liked": video.user_liked(user)})
            else:
                return JsonResponse({"code": 2000, "likes": video.count_likers(), "user_liked": video.user_liked(user)})


@api_view(['POST', 'GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_collect(request, code):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 2002, "msg": "请先登录"})
    else:
        if request.method == "POST":
            # print(request.content_type)
            # Content-type为application/json时 用下面的方法获取数据
            if request.content_type.startswith('application/json'):
                data_json = json.loads(request.body)
                video_id = data_json.get('video_id')
            else:
                video_id = request.POST.get('video_id')
            # print(video_id)
        else:
            video_id = request.query_params.get('video_id')
        if video_id is None:
            # print(video_id)
            return JsonResponse({"code": 2003, })
        else:
            video = Video.objects.get(pk=video_id)
            user = request.user
            if code == 1:
                video.switch_collect(user)
                # 用户收藏
                return JsonResponse({"code": 2001, "collects": video.count_collecters(), "user_collected": video.user_collected(user)})
            else:
                return JsonResponse({"code": 2000, "collects": video.count_collecters(), "user_collected": video.user_collected(user)})


@api_view(['POST', 'GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_video_view(request, code):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 2002, "msg": "请先登录"})
    else:
        if request.method == "POST":
            # print(request.content_type)
            # Content-type为application/json时 用下面的方法获取数据
            if request.content_type.startswith('application/json'):
                data_json = json.loads(request.body)
                video_id = data_json.get('video_id')
            else:
                video_id = request.POST.get('video_id')
            # print(video_id)
        else:
            video_id = request.query_params.get('video_id')
        if video_id is None:
            # print(video_id)
            return JsonResponse({"code": 2003, })
        else:
            video = Video.objects.get(pk=video_id)
            if code == 1:
                new_history = History.objects.update_or_create(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(video),
                    object_id=video.id,
                    defaults={'viewed_on': datetime.now()},
                )
                # new_history.save()
                # 用户观看
                return JsonResponse({"code": 2001, "msg": 'history added', })
            else:
                video.increase_view_count()
                # 观看次数
                return JsonResponse({"code": 2000, "msg": 'view count added'})


@api_view(['GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_notice(request):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 2002, "msg": "请先登录"})
    else:
        tip = Tip.objects.first()
        return JsonResponse({"code": 2000, "msg": 'ok', 'tip': tip.notice_text})


@api_view(['GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_notice_update(request, code):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 2002, "msg": "请先登录"})
    else:

        user = get_object_or_404(User, pk=request.user.pk)
        # if request.method == "POST":
        #     # print(request.content_type)
        #     # Content-type为application/json时 用下面的方法获取数据
        #     if request.content_type.startswith('application/json'):
        #         data_json = json.loads(request.body)
        #         notice_id = data_json.get('notice_id')
        #     else:
        #         notice_id = request.POST.get('notice_id')
        # else:
        notice_id = request.query_params.get('notice_id')
        if notice_id is None:
            return JsonResponse({"code": 2003, })
        else:
            print(notice_id)
            if code == 0:
                # user = get_object_or_404(User, pk=request.user.pk)
                user.notifications.get(id=notice_id).mark_as_read()
                return JsonResponse({"code": 2000, "msg": 'read 1'})
            else:
                request.user.notifications.mark_all_as_read()
                return JsonResponse({"code": 2001, "msg": 'read all'})


@api_view(['GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_check(request,):

    # user = get_object_or_404(User, pk=request.user.pk)
    # if request.method == "POST":
    #     # print(request.content_type)
    #     # Content-type为application/json时 用下面的方法获取数据
    #     if request.content_type.startswith('application/json'):
    #         data_json = json.loads(request.body)
    #         notice_id = data_json.get('notice_id')
    #     else:
    #         notice_id = request.POST.get('notice_id')
    # else:
    try:
        repair = Repair.objects.all().first()
    except:
        repair = None
    if repair is not None and repair.ok is False:
        return JsonResponse({"code": 500, "msg": 'under maintenance'})
    else:
        version = request.query_params.get('version')
        if version is None:
            return JsonResponse({"code": 403, })
        else:
            try:
                software = Software.objects.all().first()
            except:
                software = None
        if software is not None and software.version > int(version):
            new_version = software.version
            desc = software.desc
            force = software.force
            time = software.time

            return JsonResponse({"code": 400, "msg": 'need update', 'new_version': new_version, 'desc': desc, 'force': force, 'time': time})
        else:
            return JsonResponse({"code": 200, "msg": 'check ok'})


def maintenance(request):
    return render(request, 'maintenance.html')


def download(request):
    code = request.GET.get("code", None)
    if code is not None:
        messages.warning(request, "注意:  请下载 学霸空间 APP 后 扫描二维码！")

    software = Software.objects.all().first()
    desc = None
    force = None
    time = None
    if software:
        desc = software.desc.split("*")
        force = software.force
        time = software.time
    return render(request, 'download.html', context={'desc': desc, 'force': force, 'time': time})


def ad(request):
    return render(request, 'ad.html')


@csrf_exempt
def api_ad(request, code):
    if code:
        ad = get_object_or_404(AD, id=code,)
    else:
        ad = None
    if ad:
        return redirect(ad.url)
    else:
        return redirect(settings.login_url + '?next=' + request.path)

    # if not request.user.is_authenticated:
    #     return JsonResponse({"code": 2002, "msg": "请先登录"})
    # else:

        # if request.method == "POST":
        #     # print(request.content_type)
        #     # Content-type为application/json时 用下面的方法获取数据
        #     if request.content_type.startswith('application/json'):
        #         data_json = json.loads(request.body)
        #         video_id = data_json.get('video_id')
        #     else:
        #         video_id = request.POST.get('video_id')
        #     # print(video_id)
        # else:
        #     video_id = request.query_params.get('video_id')
        # if video_id is None:
        #     # print(video_id)
        #     return JsonResponse({"code": 2003, })
        # else:
        #     video = Video.objects.get(pk=video_id)
        #     user = request.user
        #     if code == 1:
        #         video.switch_like(user)
        #         # 用户喜欢
        #         return JsonResponse({"code": 2001, "likes": video.count_likers(), "user_liked": video.user_liked(user)})
        #     else:
        #         return JsonResponse({"code": 2000, "likes": video.count_likers(), "user_liked": video.user_liked(user)})


@api_view(['GET'])
@csrf_exempt
def api_user_delete(request):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 2002, "msg": "请先登录"})
    else:
        user = User.objects.filter(id=request.user.id).first()
        if user:
            user.expire = datetime.now()
            user.save()
            return JsonResponse({"code": 2000, "msg": "ok"})
        else:
            return JsonResponse({"code": 2001, "msg": "not ok"})

    #     return redirect(ad.url)
    # else:
    #     return redirect(settings.login_url + '?next=' + request.path)
