# 认证相关
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from datetime import datetime, timedelta
import json

from users.models import Token, User


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if request.method == "POST":
            # Content-type为application/json时 用下面的方法获取数据
            if request.content_type.startswith('application/json'):
                data_json = json.loads(request.body)
                token = data_json.get('tk')
            else:
                token = request.POST.get('tk')
            # print(token)
        else:
            token = request.query_params.get('tk')

        token_obj = Token.objects.filter(token=token).first()
        # print(token_obj.user)
        user_obj = Token.objects.filter(token=token).values("user__expire")

        #user_obj = token_obj.user_set.all()

        if user_obj:
            expire = user_obj[0]
            expire_time = expire["user__expire"]
            # print(expire_time)
            if expire_time is not None and expire_time - datetime.now() <= timedelta(days=0):  # 用户失效让Token一定失效
                daytime = 0
            else:  # 暂未失效
                daytime = 30
        else:  # 永久有效
            daytime = 30
        if token_obj:
            if token_obj.create_time is not None:
                if datetime.now() - token_obj.create_time > timedelta(days=daytime):  # Token失效
                    return None
                else:
                    # 返回（用户对象，token对象）
                    return (token_obj.user, token_obj)
            else:  # Token 永久有效 -不可能
                # 返回（用户对象，token对象）
                return None
        return None  # 支持匿名用户
        # raise exceptions.AuthenticationFailed('认证失败')  # 不允许匿名用户，交给dispatch中的异常处理
