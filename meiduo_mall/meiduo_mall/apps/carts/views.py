import base64
import pickle

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CartSerializers, SKUCartSerializers, CartDeleteSerializer, CartSelectedAllSerializer
from goods.models import SKU


class CartsViewSet(APIView):
    """购物车的增删改查"""

    def perform_authentication(self, request):  # 延迟到使用request.user在认证
        pass

    def post(self, request):
        serializer = CartSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        try:
            user = request.user
        except:
            user = None
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        if user and user.is_authenticated:
            """登录用户"""
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hincrby('cart_%d' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%d' % user.id, sku_id)
            pl.execute()
            # return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            """未登录
            'cart':{
                    sku_id_1:{'count':1,'selected':True},
                    sku_id_2:{'count':1,'selected':True},
                }
            """
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_str)
        return response

    def delete(self, request):
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        try:
            user = request.user
        except:
            user = None
        response = Response(serializer.data)
        if user and user.is_authenticated:
            """登录用户"""
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel('cart_%d' % user.id, sku_id)
            pl.srem('selected_%d' % user.id, sku_id)
            pl.execute()
            return Response({'message': '删除成功'}, status=status.HTTP_204_NO_CONTENT)
        else:
            """未登录"""
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({'message': '没有获取到cookeis'}, status=status.HTTP_400_BAD_REQUEST)
        if sku_id in cart_dict:
            del cart_dict[sku_id]

        if len(cart_dict.keys()):
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_str)
        else:
            response.delete_cookie('cart')
        return response

    def put(self, request):
        serializer = CartSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        try:
            user = request.user
        except:
            user = None
        response = Response(serializer.data)
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hset('cart_%d' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%d' % user.id, sku_id)
            else:
                pl.srem('selected_%d' % user.id, sku_id)
            pl.execute()
            # return Response(serializer.data)
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({'message': '没有获取到cookies'}, status=status.HTTP_400_BAD_REQUEST)
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # response = Response(serializer.data)
            response.set_cookie('cart', cart_str)
        return response

    def get(self, request):
        """构建成cart_dict：{16: {'count': 3, 'selected': True}, 11: {'count': 2, 'selected': True}}"""
        try:
            user = request.user
        except:
            user = None
        if user and user.is_authenticated:
            """登录"""
            redis_conn = get_redis_connection('cart')
            cart_redis_dict = redis_conn.hgetall('cart_%d' % user.id)
            selecteds = redis_conn.smembers('selected_%d' % user.id)
            cart_dict = {}
            for sku_id_bytes, count_bytes in cart_redis_dict.items():
                cart_dict[int(sku_id_bytes)] = {
                    'count': int(count_bytes),
                    'selected': sku_id_bytes in selecteds,
                }

        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({'message': '没有购物车数据'}, status=status.HTTP_400_BAD_REQUEST)
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']
        serializer = SKUCartSerializers(skus, many=True)
        return Response(serializer.data)


class CartSelectedAllView(APIView):
    """购物车全选"""

    def perform_authentication(self, request):
        pass

    def put(self, request):
        serializer = CartSelectedAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data.get('selected')
        try:
            user = request.user
        except:
            user = None
        response = Response(serializer.data)
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            cart_redis_dict = redis_conn.hgetall('cart_%d' % user.id)
            sku_ids = cart_redis_dict.keys()
            if selected:
                redis_conn.sadd('selected_%d' % user.id, *sku_ids)
            else:
                redis_conn.srem('selected_%d' % user.id, *sku_ids)
            # return Response(serializer.data)
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({'message': '没有获取到cookies'}, status=status.HTTP_400_BAD_REQUEST)
            for sku_id in cart_dict:
                cart_dict[sku_id]['selected'] = selected
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()  # 字典转换成字符串，
            # response = Response(serializer.data)
            response.set_cookie('cart', cart_str)
        return response
