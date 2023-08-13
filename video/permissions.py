from rest_framework import permissions

# class IsAdminUserOrReadOnly(permissions.BasePermission):
#     """
#     仅管理员用户可进行修改
#     其他用户仅可查看
#     """
#     def has_permission(self, request, view):
#         # 对所有人允许 GET, HEAD, OPTIONS 请求
#         if request.method in permissions.SAFE_METHODS:
#             return True

#         # 仅管理员可进行其他操作
#         return request.user.is_superuser


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    仅管理员用户可进行修改
    其他用户仅可查看 需登录
    """

    def has_permission(self, request, view):
        # 对所有人允许 GET, HEAD, OPTIONS 请求
        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            # 仅管理员可进行其他操作
            return request.user.is_superuser
        else:
            return False


class IsAuthenticatedAndDeleteOnly(permissions.BasePermission):
    """
    可进行修改
    用户 需登录
    """

    def has_permission(self, request, view):

        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS or request.method == 'DELETE':
                return True
            return request.user.is_superuser
        else:
            return False
