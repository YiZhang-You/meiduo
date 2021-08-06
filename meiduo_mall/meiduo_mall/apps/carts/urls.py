from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^cart/$', views.CartsViewSet.as_view()),  # sku商品展示
    url(r'^cart/selection/$', views.CartSelectedAllView.as_view()),
]
