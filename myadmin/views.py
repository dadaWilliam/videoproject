import logging
import smtplib

import datetime
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.shortcuts import *
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from article.models import Article, FileClass
from datetime import timedelta

from comment.models import Comment
from helpers import get_page_list, AdminUserRequiredMixin, ajax_required, SuperUserRequiredMixin, send_html_email
from users.models import User, Feedback
from video.models import Video, Classification
from .forms import ArticleAddForm, ArticleEditForm, FileAddForm, FileEditForm, UserLoginForm, VideoPublishForm, VideoEditForm, UserAddForm, UserEditForm, ClassificationAddForm, \
    ClassificationEditForm
from .models import MyChunkedUpload
from notifications.signals import notify

logger = logging.getLogger('my_logger')


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None and user.is_staff:
                auth_login(request, user)
                return redirect('myadmin:index')
            else:
                form.add_error('', '请输入管理员账号')
    else:
        form = UserLoginForm()
    return render(request, 'myadmin/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('myadmin:login')


class IndexView(AdminUserRequiredMixin, generic.View):
    """
    总览数据
    """

    def get(self, request):
        video_count = Video.objects.get_count()
        video_has_published_count = Video.objects.get_published_count()
        video_not_published_count = Video.objects.get_not_published_count()
        video_vip_count = Video.objects.get_vip_count()

        article_count = Article.objects.get_count()
        article_has_published_count = Article.objects.get_published_count()
        article_not_published_count = Article.objects.get_not_published_count()
        article_vip_count = Article.objects.get_vip_count()

        file_count = FileClass.objects.get_count()
        file_has_published_count = FileClass.objects.get_published_count()
        file_not_published_count = FileClass.objects.get_not_published_count()
        file_vip_count = FileClass.objects.get_vip_count()

        user_count = User.objects.count()
        user_today_count = User.objects.exclude(
            date_joined__lt=datetime.date.today()).count()
        user_vip_count = User.objects.filter(vip=True).count(),
        comment_count = Comment.objects.get_count()
        comment_today_count = Comment.objects.get_today_count()

        feedback_count = Feedback.objects.get_count()
        feedback_today_count = Feedback.objects.exclude(
            timestamp__lt=datetime.date.today()).count()

        data = {"video_count": video_count,
                "video_has_published_count": video_has_published_count,
                "video_not_published_count": video_not_published_count,
                "video_vip_count": video_vip_count,

                "article_count": article_count,
                "article_has_published_count": article_has_published_count,
                "article_not_published_count": article_not_published_count,
                "article_vip_count": article_vip_count,

                "file_count": file_count,
                "file_has_published_count": file_has_published_count,
                "file_not_published_count": file_not_published_count,
                "file_vip_count": file_vip_count,

                "user_count": user_count,
                "user_today_count": user_today_count,
                "user_vip_count": user_vip_count[0],

                "comment_count": comment_count,
                "comment_today_count": comment_today_count,

                "feedback_count": feedback_count,
                "feedback_today_count": feedback_today_count
                }
        return render(self.request, 'myadmin/index.html', data)

    def dispatch(self, request, *args, **kwargs):
        key_tk: str = request.GET.get('tk', '')

        if key_tk:
            user = User.objects.filter(token__token=key_tk).first()
            if user:
                if user.expire:
                    if datetime.now() - user.expire >= timedelta(days=0):
                        messages.warning(request, "用户已失效，请联系管理员")
                        return render(request, 'registration/login.html', {'form': UserLoginForm()})
                    else:
                        auth_login(request, user)
                else:
                    auth_login(request, user)

        return super().dispatch(request, *args, **kwargs)


class AddVideoView(SuperUserRequiredMixin, TemplateView):
    template_name = 'myadmin/video_add.html'


class MyChunkedUploadView(ChunkedUploadView):
    model = MyChunkedUpload
    field_name = 'the_file'


class MyChunkedUploadCompleteView(ChunkedUploadCompleteView):
    model = MyChunkedUpload

    def on_completion(self, uploaded_file, request):
        print('uploaded--->', uploaded_file.name)
        pass

    def get_response_data(self, chunked_upload, request):
        video = Video.objects.create(file=chunked_upload.file)
        return {'code': 0, 'video_id': video.id, 'msg': 'success'}


class VideoPublishView(SuperUserRequiredMixin, generic.UpdateView):
    model = Video
    form_class = VideoPublishForm
    template_name = 'myadmin/video_publish.html'

    def get_context_data(self, **kwargs):
        context = super(VideoPublishView, self).get_context_data(**kwargs)
        clf_list = Classification.objects.all().values()
        clf_data = {'clf_list': clf_list}
        context.update(clf_data)
        return context

    def get_success_url(self):
        return reverse('myadmin:video_publish_success')


class VideoPublishSuccessView(generic.TemplateView):
    template_name = 'myadmin/video_publish_success.html'


class VideoEditView(SuperUserRequiredMixin, generic.UpdateView):
    model = Video
    form_class = VideoEditForm
    template_name = 'myadmin/video_edit.html'

    def get_context_data(self, **kwargs):
        context = super(VideoEditView, self).get_context_data(**kwargs)
        clf_list = Classification.objects.all().values()
        clf_data = {'clf_list': clf_list}
        context.update(clf_data)
        return context

    def get_success_url(self):
        messages.success(self.request, "保存成功")
        return reverse('myadmin:video_edit', kwargs={'pk': self.kwargs['pk']})


@ajax_required
@require_http_methods(["POST"])
def video_delete(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无删除权限"})
    video_id = request.POST['video_id']
    instance = Video.objects.get(id=video_id)
    instance.delete()
    return JsonResponse({"code": 0, "msg": "success"})


class VideoListView(AdminUserRequiredMixin, generic.ListView):
    model = Video
    template_name = 'myadmin/video_list.html'
    context_object_name = 'video_list'
    paginate_by = 10
    q = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(VideoListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return Video.objects.get_search_list(self.q)

###


class ArticleListView(AdminUserRequiredMixin, generic.ListView):
    model = Article
    template_name = 'myadmin/article_list.html'
    context_object_name = 'article_list'
    paginate_by = 10
    q = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return Article.objects.filter(title__contains=self.q)


class ArticleAddView(SuperUserRequiredMixin, generic.View):
    def get(self, request):
        form = ArticleAddForm()
        return render(self.request, 'myadmin/article_add.html', {'form': form})

    def post(self, request):
        form = ArticleAddForm(data=request.POST, files=request.FILES)
        if form.is_valid():

            form.save(commit=True)
            return render(self.request, 'myadmin/article_add_success.html')
        return render(self.request, 'myadmin/article_add.html', {'form': form})
    # def get_success_url(self):
    #     return reverse('myadmin:video_publish_success')


@ajax_required
@require_http_methods(["POST"])
def article_delete(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无删除权限"})
    article_id = request.POST['article_id']
    instance = Article.objects.get(id=article_id)
    instance.delete()
    return JsonResponse({"code": 0, "msg": "success"})


class ArticleEditView(SuperUserRequiredMixin, generic.UpdateView):
    model = Article
    form_class = ArticleEditForm
    template_name = 'myadmin/article_edit.html'

    def get_success_url(self):
        messages.success(self.request, "保存成功")
        return reverse('myadmin:article_edit', kwargs={'pk': self.kwargs['pk']})


###
class FileListView(AdminUserRequiredMixin, generic.ListView):
    model = FileClass
    template_name = 'myadmin/file_list.html'
    context_object_name = 'file_list'
    paginate_by = 10
    q = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(FileListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return FileClass.objects.filter(file__contains=self.q)


class FileAddView(SuperUserRequiredMixin, generic.View):
    def get(self, request):
        form = FileAddForm()

        return render(self.request, 'myadmin/file_add.html', {'form': form})

    def post(self, request):
        form = FileAddForm(data=request.POST, files=request.FILES)
        if form.is_valid():

            form.save(commit=True)
            return render(self.request, 'myadmin/file_add_success.html')
        return render(self.request, 'myadmin/file_add.html', {'form': form})


@ajax_required
@require_http_methods(["POST"])
def file_delete(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无删除权限"})
    file_id = request.POST['file_id']
    instance = FileClass.objects.get(id=file_id)
    instance.delete()
    return JsonResponse({"code": 0, "msg": "success"})


class FileEditView(SuperUserRequiredMixin, generic.UpdateView):
    model = FileClass
    form_class = FileEditForm
    template_name = 'myadmin/file_edit.html'

    def get_success_url(self):
        messages.success(self.request, "保存成功")
        return reverse('myadmin:file_edit', kwargs={'pk': self.kwargs['pk']})
 #####


class ClassificationListView(AdminUserRequiredMixin, generic.ListView):
    model = Classification
    template_name = 'myadmin/classification_list.html'
    context_object_name = 'classification_list'
    paginate_by = 10
    q = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ClassificationListView,
                        self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return Classification.objects.filter(title__contains=self.q)


class ClassificationAddView(SuperUserRequiredMixin, generic.View):
    def get(self, request):
        form = ClassificationAddForm()
        return render(self.request, 'myadmin/classification_add.html', {'form': form})

    def post(self, request):
        form = ClassificationAddForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(commit=True)
            return render(self.request, 'myadmin/classification_add_success.html')
        return render(self.request, 'myadmin/classification_add.html', {'form': form})


@ajax_required
@require_http_methods(["POST"])
def classification_delete(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无删除权限"})
    classification_id = request.POST['classification_id']
    instance = Classification.objects.get(id=classification_id)
    instance.delete()
    return JsonResponse({"code": 0, "msg": "success"})


class ClassificationEditView(SuperUserRequiredMixin, generic.UpdateView):
    model = Classification
    form_class = ClassificationEditForm
    template_name = 'myadmin/classification_edit.html'

    def get_success_url(self):
        messages.success(self.request, "保存成功")
        return reverse('myadmin:classification_edit', kwargs={'pk': self.kwargs['pk']})


class CommentListView(AdminUserRequiredMixin, generic.ListView):
    model = Comment
    template_name = 'myadmin/comment_list.html'
    context_object_name = 'comment_list'
    paginate_by = 10
    q = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CommentListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return Comment.objects.filter(content__contains=self.q).order_by('-timestamp')


@ajax_required
@require_http_methods(["POST"])
def comment_delete(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无删除权限"})
    comment_id = request.POST['comment_id']
    instance = Comment.objects.get(id=comment_id)
    instance.delete()
    return JsonResponse({"code": 0, "msg": "success"})


class UserListView(AdminUserRequiredMixin, generic.ListView):
    model = User
    template_name = 'myadmin/user_list.html'
    context_object_name = 'user_list'
    paginate_by = 10
    q = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return User.objects.filter(username__contains=self.q).order_by('-date_joined')


class UserAddView(SuperUserRequiredMixin, generic.View):
    def get(self, request):
        form = UserAddForm()
        return render(self.request, 'myadmin/user_add.html', {'form': form})

    def post(self, request):
        form = UserAddForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            return render(self.request, 'myadmin/user_add_success.html')
        return render(self.request, 'myadmin/user_add.html', {'form': form})


class UserEditView(SuperUserRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'myadmin/user_edit.html'

    def get_success_url(self):
        messages.success(self.request, "保存成功")
        return reverse('myadmin:user_edit', kwargs={'pk': self.kwargs['pk']})


@ajax_required
@require_http_methods(["POST"])
def user_delete(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无删除权限"})
    user_id = request.POST['user_id']
    instance = User.objects.get(id=user_id)
    if instance.is_superuser:
        return JsonResponse({"code": 1, "msg": "不能删除管理员"})
    instance.delete()
    return JsonResponse({"code": 0, "msg": "success"})


class SubscribeView(SuperUserRequiredMixin, generic.View):

    def get(self, request):
        video_list = Video.objects.get_published_list()
        return render(request, "myadmin/subscribe.html", {'video_list': video_list})

    def post(self, request):
        if not request.user.is_superuser:
            return JsonResponse({"code": 1, "msg": "无权限"})
        video_id = request.POST['video_id']
        video = Video.objects.get(id=video_id)
        subject = video.title
        context = {'video': video, 'site_url': settings.SITE_URL}
        html_message = render_to_string('myadmin/mail_template.html', context)
        email_list = User.objects.filter(
            subscribe=True).values_list('email', flat=True)
        # 分组
        email_list = [email_list[i:i + 2]
                      for i in range(0, len(email_list), 2)]

        if email_list:
            for to_list in email_list:
                try:
                    send_html_email(subject, html_message, to_list)
                except smtplib.SMTPException as e:
                    logger.error(e)
                    return JsonResponse({"code": 1, "msg": "发送失败"})
            return JsonResponse({"code": 0, "msg": "success"})
        else:
            return JsonResponse({"code": 1, "msg": "邮件列表为空"})


class FeedbackListView(AdminUserRequiredMixin, generic.ListView):
    model = Feedback
    template_name = 'myadmin/feedback_list.html'
    context_object_name = 'feedback_list'
    paginate_by = 10
    q = ''

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(FeedbackListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        context['page_list'] = page_list
        context['q'] = self.q
        return context

    def get_queryset(self):
        self.q = self.request.GET.get("q", "")
        return Feedback.objects.filter(content__contains=self.q).order_by('-timestamp')


@ajax_required
@require_http_methods(["POST"])
def feedback_delete(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无删除权限"})
    feedback_id = request.POST['feedback_id']
    instance = Feedback.objects.get(id=feedback_id)
    instance.delete()
    return JsonResponse({"code": 0, "msg": "success"})


@ajax_required
@require_http_methods(["POST"])
def advertising(request):
    if not request.user.is_superuser:
        return JsonResponse({"code": 1, "msg": "无权限"})
    video_id = request.POST['video_id']
    video = Video.objects.filter(id=video_id).first()
    if video:
        if video.vip:
            notify.send(
                request.user,
                recipient=User.objects.filter(vip=video.vip),
                verb='通知你观看',
                target=video,
                # action_object=new_comment,
            )
        else:
            notify.send(
                request.user,
                recipient=User.objects.filter(),
                verb='通知你观看',
                target=video,
                # action_object=new_comment,
            )

        # # 处理 POST 请求
        # notify.send(
        #     request.user,
        #     recipient=User.objects.filter(vip=video.vip),
        #     verb='通知你观看',
        #     target=video,
        #     # action_object=new_comment,
        # )
        return JsonResponse({"code": 0, "msg": "success"})
    return JsonResponse({"code": 2, "msg": "错误"})
