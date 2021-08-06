import re

from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    ⾃定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_acount(count):
    """判断是手机号还是用户名登录"""
    try:
        if re.match(r"^1[3-9]\d{9}", count):
            user = User.objects.get(mobile=count)
        else:
            user = User.objects.get(username=count)
    except User.DoesNotExist:
        return None
    return user


class UsernameOrMobileAuthBackend(ModelBackend):
    """修改django认证类，实现多账户登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_acount(username)
        if user and user.check_password(password):
            return user
