from django.http import Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
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
        tokens = Token.objects.all()

        try:
            repair = Repair.objects.all()[0]
        except:
            repair = None
        if repair is None or repair.ok:  # not repair
            key_tk: str = request.GET.get('tk', '')
            #print("key_tk "+key_tk)

            if url.startswith('/static/') or url.startswith('/api/') or url == '/api-check/' or url == '/download/' or url == '/users/qrcode/' or url == '/users/check-qrcode/' or url.startswith('/ws/'):
                return self.get_response(request)
            if not request.user.is_authenticated and request.path_info not in self.open_urls:
                if url.startswith('/upload/'):
                    for token in tokens:
                        # print(token.token)
                        if key_tk and key_tk == token.token:
                            return self.get_response(request)
                        else:
                            pass
                    return redirect(self.login_url + '?next=' + request.path)
                else:
                    return redirect(self.login_url + '?next=' + request.path)
            return self.get_response(request)
        else:
            if url.startswith('/admin/') or url.startswith('/static/') or url == '/api-check/' or url == '/download/' or url == '/users/qrcode/' or url == '/users/check-qrcode/' or url.startswith('/ws/'):
                return self.get_response(request)

            else:
                if repair.ok_time is None:
                    context = {'ok_time': '待定'}
                else:
                    context = {'ok_time': repair.ok_time}

                return render(request, 'maintenance.html', context)
