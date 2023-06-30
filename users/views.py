from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random
import string
import io
from qrcode.image.svg import SvgPathFillImage
from qrcode import make as qr_code_make
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

from videoproject.settings import SITE_URL

from .models import Feedback, QRcode, Token, User

from .forms import ProfileForm, SignUpForm, UserLoginForm, ChangePwdForm, SubscribeForm, FeedbackForm


from io import BytesIO

User = get_user_model()


def generate_random_string(length):
    # Define the characters that can be used
    characters = string.ascii_letters + string.digits
    # Generate the random string
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string


@ratelimit(key='ip', rate='10/m')
def login(request):
    was_limited = getattr(request, 'limited', False)

    if request.method == 'POST':

        next = request.POST.get('next', '/')
        form = UserLoginForm(request=request, data=request.POST)

        if was_limited:
            messages.warning(request, "操作太频繁了，请1分钟后再试")
            return render(request, 'registration/login.html', {'form': form, 'next': next})
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            # user = authenticate(
            #     request, username=request.POST["username"], password=request.POST["password"])

            if user is not None:
                if user.expire is not None:
                    if datetime.now() - user.expire >= timedelta(days=0):
                        messages.warning(request, "用户已失效，请联系管理员")
                        # return HttpResponse("用户已失效，请联系管理员")
                        # return render(request, 'registration/login.html', {'form': form, 'next': next, })
                    else:
                        auth_login(request, user)
                        session_key = request.session.session_key  # 单一设备登陆
                        for session in Session.objects.filter(~Q(session_key=session_key), expire_date__gte=timezone.now()):
                            data = session.get_decoded()
                            if data.get('_auth_user_id', None) == str(request.user.id):
                                session.delete()
                        # return redirect('home')
                        return redirect(next)
                else:
                    auth_login(request, user)
                    session_key = request.session.session_key  # 单一设备登陆
                    for session in Session.objects.filter(~Q(session_key=session_key), expire_date__gte=timezone.now()):
                        data = session.get_decoded()
                        if data.get('_auth_user_id', None) == str(request.user.id):
                            session.delete()
                    # return redirect('home')
                    return redirect(next)
        else:
            print(form.errors)
    else:
        next = request.GET.get('next', '/')
        form = UserLoginForm()
        if was_limited:
            messages.warning(request, "操作太频繁了，请1分钟后再试")
            return render(request, 'registration/login.html', {'form': form, 'next': next})

    print(next)
    return render(request, 'registration/login.html', {'form': form, 'next': next})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # form.save()
            #username = form.cleaned_data.get('username')
            #raw_password1 = form.cleaned_data.get('password1')
            #user = authenticate(username=username, password=raw_password1)
            #auth_login(request, user)
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('home')


def change_password(request):
    if request.method == 'POST':
        form = ChangePwdForm(request.user, request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.is_staff and not user.is_superuser:
                user.save()
                update_session_auth_hash(request, user)  # 更新session 非常重要！
                messages.success(request, '修改成功')
                return redirect('users:change_password')
            else:
                messages.warning(request, '无权修改管理员密码')
                return redirect('users:change_password')
        else:
            print(form.errors)
    else:
        form = ChangePwdForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


class ProfileView(LoginRequiredMixin, AuthorRequiredMixin, generic.UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'users/profile.html'

    def get_success_url(self):
        messages.success(self.request, "保存成功")
        return reverse('users:profile', kwargs={'pk': self.request.user.pk})


class SubscribeView(LoginRequiredMixin, AuthorRequiredMixin, generic.UpdateView):
    model = User
    form_class = SubscribeForm
    template_name = 'users/subscribe.html'

    def get_success_url(self):
        messages.success(self.request, "保存成功")
        return reverse('users:subscribe', kwargs={'pk': self.request.user.pk})


class FeedbackView(LoginRequiredMixin, generic.CreateView):

    model = Feedback
    form_class = FeedbackForm
    template_name = 'users/feedback.html'

    @ratelimit(key='ip', rate='2/m')
    def post(self, request, *args, **kwargs):
        was_limited = getattr(request, 'limited', False)
        if was_limited:
            messages.warning(self.request, "操作太频繁了，请1分钟后再试")
            return render(request, 'users/feedback.html', {'form': FeedbackForm()})
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "提交成功")
        return reverse('users:feedback')


class CollectListView(generic.ListView):
    model = User
    template_name = 'users/collect_videos.html'
    context_object_name = 'video_list'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CollectListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        return context

    def get_queryset(self):
        user = self.request.user
        if user.vip:
            videos = user.collected_videos.all()
        else:
            videos = user.collected_videos.all().filter(vip=user.vip)
        return videos
        # # user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        # videos = user.collected_videos.all()
        # return videos


class LikeListView(generic.ListView):
    model = User
    template_name = 'users/like_videos.html'
    context_object_name = 'video_list'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LikeListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        return context

    def get_queryset(self):
        # user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        user = self.request.user
        if user.vip:
            videos = user.liked_videos.all()
        else:
            videos = user.liked_videos.all().filter(vip=user.vip)
        return videos


def get_qr_image_for_user(qr_url: str) -> str:
    svg_image_obj = qr_code_make(qr_url, image_factory=SvgPathFillImage)
    image = io.BytesIO()
    svg_image_obj.save(stream=image)
    base64_image = base64.b64encode(image.getvalue()).decode()
    return 'data:image/svg+xml;utf8;base64,' + base64_image


@ajax_required
@require_http_methods(["POST", "GET"])
def generate_QRcode(request):
    ip = request.META.get('REMOTE_ADDR', None)
    code = generate_random_string(10)
    QRcode.objects.update_or_create(ip=ip, defaults={'code': code, })

    qrcode = get_qr_image_for_user(
        "http://" + SITE_URL + "/download?"+"code="+code)
    # factory = qrcode.image.svg.SvgImage
    # # request.POST.get("qr_text", ""),
    # img = qrcode.make("https://123456789",
    #                   image_factory=factory)
    # # img.save('QRCode.png')
    # stream = BytesIO()
    # # img.save
    # # encoded_string = base64.b64encode(img).decode('ascii')
    # img.save(stream)
    # print(type(stream.getvalue().decode()))
    # context["svg"] = stream.getvalue().decode()
    # if not request.user.is_authenticated:
    #     return JsonResponse({"code": 1, "msg": "请先登录"})
    # video_id = request.POST['video_id']
    # video = Video.objects.get(pk=video_id)
    # user = request.user
    # video.switch_collect(user)
    # return render(request, "index.html", context=context)
    a = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" stroke="green" stroke-width="4" fill="yellow" /></svg>'
    return JsonResponse({"code": 0, "qrcode": qrcode, })


# @ajax_required
@require_http_methods(["GET"])
def check_QRcode(request,):
    next = request.POST.get('next', '/')
    # Authenticate the client here...
    # ip = request.META.get('REMOTE_ADDR', None)
    code = request.GET.get('code', None)
    token = request.GET.get('token', None)
    qrcode = None
    user = User.objects.filter(token__token=token)
    user_obj = Token.objects.filter(token=token).values("user__expire")
    if user_obj:
        expire = user_obj[0]
        expire_time = expire["user__expire"]
        # print(expire_time)
        if expire_time is not None and expire_time - datetime.now() <= timedelta(days=0):  # 用户失效
            messages.warning(request, "用户失效或扫码出错")
            return render(request, 'registration/login.html', {'form': form, 'next': next})
        else:  # 暂未失效
            # QRcode.objects.update_or_create(ip=ip, defaults={'code': code, })
            qrcode = QRcode.objects.get(code=code)
    if qrcode is not None and qrcode.create_time - datetime.now() <= timedelta(minutes=300):
        username = user[0].username

        login(user)
        print(request)
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     f"client-{client_id}",
        #     {
        #         "type": "login",
        #         "client_id": client_id,
        #     }
        # )
        return JsonResponse({"code": 0, "qrcode": '1', })
    else:
        return JsonResponse({"code": 0, "qrcode": qrcode, })

    # qrcode = get_qr_image_for_user(
    #     "xueba//请打开学霸空间APP扫描二维码登录//"+code+"//"+datetime.now().isoformat())

    # return HttpResponse("Client authenticated!")
    # return JsonResponse({"code": 0, "qrcode": qrcode, })


# views.py


# def authenticate_and_notify(request, client_id):
#     next = request.POST.get('next', '/')
#     # Authenticate the client here...

#     # Once authenticated, send a WebSocket message to the client
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         f"client-{client_id}",
#         {
#             "type": "login",
#             "client_id": client_id,
#         }
#     )
#     return redirect(next)
