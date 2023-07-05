import os
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from article.models import FileClass
from users.models import Token, Repair
from django.shortcuts import render


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = settings.LOGIN_URL
        self.repair_url = settings.REPAIR_URL
        self.open_urls = [self.login_url] + getattr(settings, 'OPEN_URLS', [])

    def __call__(self, request, ):

        url = request.path_info
        # tokens = Token.objects.all()
        condition = url.startswith('/static/') or url.startswith(
            '/api/') or url == '/api-check/' or url == '/download/' or url == '/users/qrcode/' or url == '/users/check-qrcode/' or url == '/users/scan-login/'

        repair = Repair.objects.all().first()

        if not repair or repair.ok:  # not repair
            key_tk: str = request.GET.get('tk', '')
            #print("key_tk "+key_tk)
            if condition or url in self.open_urls:  # all pass no token, no login
                return self.get_response(request)
            else:
                if request.user.is_authenticated:
                    # print('here')
                    # print(request)
                    # print('here2')
                    if request.user.is_superuser:

                        return self.get_response(request)

                    elif url.startswith('/upload/file/'):
                        code = request.GET.get('code', None)
                        if code:
                            # print('here code ')
                            filename = 'file/' + url.split('/')[-2]
                            file = FileClass.objects.filter(
                                file=filename, code=code,).first()
                        else:
                            # print('here no code ')
                            filename = 'file/' + url.split('/')[-2]
                            file = FileClass.objects.filter(
                                file=filename,).first()
                            # print(file.code)
                            if file and file.code:
                                return render(request, "wrong.html",)

                        # print(file)
                        if file:
                            # print(filename)
                            # print("file")
                            # print(file.file)
                            file.increase_view_count()
                            return self.get_response(request)

                            # for file in files:
                            #
                            #     if file and filename and filename == file.file.name:
                            #         file.increase_view_count()
                            #         return self.get_response(request)
                            # return render(request, "404.html",)
                        else:
                            return render(request, "wrong.html",)

                    return self.get_response(request)

                elif not request.user.is_authenticated:
                    if url.startswith('/upload/'):
                        token = Token.objects.filter(token=key_tk).first()
                        if token:
                            if url.startswith('/upload/file/'):
                                code = request.GET.get('code', None)
                                if code:
                                    filename = 'file/' + url.split('/')[-2]
                                    file = FileClass.objects.filter(
                                        file=filename, code=code,).first()
                                else:

                                    filename = 'file/' + url.split('/')[-2]
                                    file = FileClass.objects.filter(
                                        file=filename,).first()

                                    if file and file.code:
                                        return render(request, "wrong.html",)

                                if file:
                                    file.increase_view_count()
                                    return self.get_response(request)
                                else:
                                    return render(request, "wrong.html",)
                            return self.get_response(request)

                    return redirect(self.login_url + '?next=' + request.path)
                else:
                    return redirect(self.login_url + '?next=' + request.path)
            # return self.get_response(request)
        else:
            if condition:
                return self.get_response(request)

            else:
                if repair.ok_time is None:
                    context = {'ok_time': '待定'}
                else:
                    context = {'ok_time': repair.ok_time}

            return render(request, 'maintenance.html', context)
