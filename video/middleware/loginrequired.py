from django.shortcuts import redirect
from django.conf import settings
from users.models import Token

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = settings.LOGIN_URL
        self.open_urls = [self.login_url] + getattr(settings, 'OPEN_URLS', [])

    def __call__(self, request):

        url = request.path_info
        tokens = Token.objects.all()
        key_tk:String = request.GET.get('tk','');
        #print("key_tk "+key_tk)

        if url.startswith('/static/') or url.startswith('/api/'):
            return self.get_response(request)
        if not request.user.is_authenticated and request.path_info not in self.open_urls:
            if url.startswith('/upload/'):
                for token in tokens:
                    #print(token.token)
                    if key_tk and key_tk == token.token:
                        return self.get_response(request)
                    else:
                        pass
                return redirect(self.login_url + '?next=' + request.path)
            else:
                return redirect(self.login_url + '?next=' + request.path)
        return self.get_response(request)