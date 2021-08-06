from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('addresses', views.AddressViewSet, base_name='addresses')

urlpatterns = [
    # 用户注册
    url(r'users/$', views.UserView.as_view()),
    # 判断用户是否存在
    url(r'username/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # # 判断手机号是否存在
    url(r'mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

    # url(r'^authorizations/$', obtain_jwt_token),  # JWT登录
    url(r'^authorizations/$', views.UserAuthorizeView.as_view()),  # 内部认证代码还是Django  登录成功生成token

    url(r'^user/$', views.UserDetailView.as_view()),  # 展示用户个人信息
    url(r'^email/$', views.EmailView.as_view()),  # 添加邮箱信息
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),  # 用户邮箱解密，更改邮箱的校验状态
]

urlpatterns += router.urls
