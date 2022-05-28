# 认证相关
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from datetime import datetime, timedelta

from users.models import Token
class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('tk')
        token_obj = Token.objects.filter(token=token).first()
        if token_obj:
            if token_obj.create_time is not None:
                if datetime.now() - token_obj.create_time > timedelta(days=30):  # Token失效
                    return None
                else:
                    # 返回（用户对象，token对象）
                    return (token_obj.user, token_obj)
            else: # Token 永久有效 -不可能
                # 返回（用户对象，token对象）
                return None
        return None  # 支持匿名用户
        #raise exceptions.AuthenticationFailed('认证失败')  # 不允许匿名用户，交给dispatch中的异常处理