from django.contrib import admin
from users.models import User    # 自己创建的模型类
from django.contrib.auth.admin import UserAdmin

class UserInfoAdmin(UserAdmin):
	# 这是在管理页面中想要显示的内容
    list_display = ['username', 'expire', 'date_joined', 'last_login']
	# 分页
    list_per_page = 10
    # 设置 只读 的字段

    # 后台显示的字段
    fieldsets = [
               (None, {'fields':['username', 'password', 'email', 'is_staff', 'is_superuser']}),
               ('用户活跃信息', {'fields': ['date_joined', 'last_login','expire','user_permissions', 'groups']}),
    ]
# 注册时要将这两个模型类同时注册
admin.site.register(User, UserInfoAdmin)

