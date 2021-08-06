from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),  # 确认订单
    url(r'^orders/$', views.CommitOrderView.as_view()),  # 商品生成订单

]
