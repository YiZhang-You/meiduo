"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import xadmin
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('verifications.urls')),  # 发送短信
    url(r'^', include('users.urls', namespace='users')),  # 用户模块
    url(r'^oauth/', include('oauth.urls')),  # QQ模块
    url(r'^', include('areas.urls')),  # 省市区
    url(r'^', include('goods.urls')),  # 商品
    # url(r'^', include('contents.urls')),  # 广告内容
    url(r'^', include('carts.urls')),  # 购物车
    url(r'^', include('orders.urls')),  # 订单
    url(r'^', include('payment.urls')),  # 支付宝
    url(r'xadmin/', include(xadmin.site.urls)),  # xadmin
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),  # 富文本
]

# www.meiduo.site
# api.meiduo.site
# http://192.168.216.137:8888/group1/M00/00/01/CtM3BVrMexWAfodJAAAhg8MeEWU8364862
# http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRdOiAUBFXAAYJrpessGQ2842711
# superadmin    123456abc

# python ../../manage.py crontab show
# python ../../manage.py crontab add
# python ../../manage.py crontab remove
