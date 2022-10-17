from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from requests import Response


from video.serializers import *

from helpers import get_page_list, ajax_required
from .forms import CommentForm
from .models import Video, Classification
from history.models import History
from users.models import User,Token

from video.permissions import IsAdminUserOrReadOnly
from rest_framework import viewsets, generics
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import authenticate

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes

from datetime import datetime, timedelta
from history.mixins import ObjectViewMixin
import json
from django.contrib.contenttypes.models import ContentType

def page_not_found(request, exception):
    return render(request, "404.html",)

#api
class UserViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    #permission_classes = [IsAdminUserOrReadOnly]

class ClassificationViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = Classification.objects.all()
    serializer_class = ClassificationSerializer
    permission_classes = (IsAuthenticated,)
    #permission_classes = [IsAdminUserOrReadOnly]

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.filter(status=0).order_by('-create_time')
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)
    # permission_classes = [IsAdminUserOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['title','classification__title']

class VideoIndexShowViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.get_index_show()
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)

class VideoCollectedViewSet(generics.ListCreateAPIView):
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        # print(self.kwargs.get('video_id'))
        videos = user.collected_videos.all()
        return videos

class VideoLikedViewSet(generics.ListCreateAPIView):
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        # print(self.kwargs.get('video_id'))
        videos = user.collected_videos.all()
        return videos

class VideoRecommendViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.get_recommend_list()
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)

class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all().order_by('-viewed_on')
    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticated,)
    # permission_classes = [IsAdminUserOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['user__id',]

class NotificationViewSet(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        code = self.kwargs.get('code')
        # print(self.kwargs.get('video_id'))
        if code == 0:
            notifications = Notification.objects.filter(recipient=user,unread=True)
        elif code == 1:
            notifications = Notification.objects.filter(recipient=user, unread=False)
        else:
            notifications = Notification.objects.filter(recipient=user,)
        return notifications

# class NotificationViewSet(viewsets.ModelViewSet):
#     queryset = Notification.objects.all()
#     serializer_class = NotificationSerializer
#     permission_classes = (IsAuthenticated,)
#     # permission_classes = [IsAdminUserOrReadOnly]
#
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['user__id',]

#login token
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
        #print('username:',username)
        #print('pwd:',pwd)
        user_obj = authenticate(username=username, password=pwd)
        #user_obj = User.objects.filter(username=username, password=pwd).first()
        if user_obj: # 如果用户存在，那么生成token并更新
            if user_obj.expire is not None:
                if datetime.now() - user_obj.expire >= timedelta(days=0): #用户失效
                    res['code'] = 1002
                    res['msg'] = 'User expired'
                else:
                    token = generate_token(username)

                    Token.objects.update_or_create(user=user_obj, defaults={'token': token, })
                    res['user'] = user_obj.id
                    res['token'] = token
            else:#永久有效用户
                token = generate_token(username)
                Token.objects.update_or_create(user=user_obj, defaults={'token': token})
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
        context = super(IndexView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        classification_list = Classification.objects.filter(status=True).order_by('-time').values()
        context['c'] = self.c
        context['classification_list'] = classification_list
        context['page_list'] = page_list
        return context

    def get_queryset(self):
        self.c = self.request.GET.get("c", None)
        if self.c:
            classification = get_object_or_404(Classification, pk=self.c)
            return classification.video_set.all().order_by('-create_time').filter(status=0)
        else:
            return Video.objects.filter(status=0).order_by('-create_time')


class SearchListView(generic.ListView):
    model = Video
    template_name = 'video/search.html'
    context_object_name = 'video_list'
    paginate_by = 8
    q = ''

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return Video.objects.filter(title__contains=self.q).filter(status=0)

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
        obj = super().get_object()
        obj.increase_view_count()
        return obj

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        recommend_list = Video.objects.get_recommend_list()
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

@api_view(['POST','GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_like(request,code):
    if not request.user.is_authenticated:
        return JsonResponse({"code": 2002, "msg": "请先登录"})
    else:
        if request.method == "POST":
            #print(request.content_type)
            # Content-type为application/json时 用下面的方法获取数据
            if request.content_type.startswith('application/json'):
                data_json = json.loads(request.body)
                video_id = data_json.get('video_id')
            else:
                video_id = request.POST.get('video_id')
            #print(video_id)
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
                #用户喜欢
                return JsonResponse({"code": 2001, "likes": video.count_likers(), "user_liked": video.user_liked(user)})
            else:
                return JsonResponse({"code": 2000, "likes": video.count_likers(), "user_liked": video.user_liked(user)})

@api_view(['POST','GET'])
# @permission_classes((AllowAny, ))
@csrf_exempt
def api_collect(request,code):
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
            #print(video_id)
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
                #用户收藏
                return JsonResponse({"code": 2001, "collects": video.count_collecters(), "user_collected": video.user_collected(user)})
            else:
                return JsonResponse({"code": 2000, "collects": video.count_collecters(), "user_collected": video.user_collected(user)})

@api_view(['POST','GET'])
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
            #print(video_id)
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
                #用户观看
                return JsonResponse({"code": 2001, "msg": 'history added',})
            else:
                video.increase_view_count()
                #观看次数
                return JsonResponse({"code": 2000, "msg": 'view count added'})

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

def maintenance(request):
    return render(request, 'maintenance.html' );