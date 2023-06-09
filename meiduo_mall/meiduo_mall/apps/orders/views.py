from decimal import Decimal

from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection

from goods.models import SKU

from .serializers import OrderSettlementSerializer, CommitOrderSerializer


class CommitOrderView(CreateAPIView):
    """商品生成订单"""
    permission_classes = [IsAuthenticated]
    serializer_class = CommitOrderSerializer


class OrderSettlementView(APIView):
    """订单结算"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%d' % user.id)
        cart_selected = redis_conn.smembers('selected_%d' % user.id)
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])  # {'商品ID','商品数量'}
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
        freight = Decimal('10.00')
        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)
