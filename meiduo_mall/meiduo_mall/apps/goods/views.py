from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_haystack.viewsets import HaystackViewSet


from .serializers import SKUSerializer, UserBrowseHistoriesSerializers, UserGetBrowseHistoriesSerializers, \
    SKUIndexSerializer
from .models import SKU


class SKUListView(ListAPIView):
    """sku商品展示"""
    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(is_launched=True, category_id=category_id)


class UserBrowseHistoriesView(CreateAPIView):
    """用户浏览记录"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserBrowseHistoriesSerializers

    def get(self, request):
        redis_conn = get_redis_connection('history')
        user = request.user
        sku_ids = redis_conn.lrange('history_%d' % user.id, 0, -1)  # 获取全部的数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        serializer = UserGetBrowseHistoriesSerializers(sku_list, many=True)
        return Response(serializer.data)



class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer
# YzjDDGMMB3wltgmicsgyJAFU%2Bigeo9eXVXoVkw%2FARIZNbaWAhgCysByAdq76put4Fxap5MIqqhcYLMvEuEcoKvtU1%2BmAXH%2Fqr%2BEd5Qwb1rxJ%2FL2eJA7nunMj1cGh5bjKmb9xVkfFbEJ3JB5da2pnemdytPKLNokhRUlKJ%2FihDbQVotkLffTtbY7t1%2FjB%2Fp3l16MrnSkNhSiOuwEIgXc0GDOkFDYPyAlxYy5%2BC0Jlk1nKRPiGGUsPZmln7CTbu1FGK4xw3OFmN4kJc%2Fr3uSqTj5VbPeEuMsQa0k8uhFx64PvDgnhUPi%2FGXFiXsgIXYKBmAo%2FpGdRezY3q8qydYMGUZQ%3D%3D
