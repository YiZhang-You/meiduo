from rest_framework import serializers
from django_redis import get_redis_connection
from drf_haystack.serializers import HaystackSerializer

from .models import SKU
from .search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):
    """sku商品序列化"""

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']

class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')

class UserBrowseHistoriesSerializers(serializers.Serializer):
    """用户浏览记录保存"""
    sku_id = serializers.IntegerField(label='商品编号', min_value=1)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("商品不存在")
        return value

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        sku_id = validated_data.get('sku_id')
        redis_coon = get_redis_connection('history')
        pl = redis_coon.pipeline()
        pl.lrem('history_%s' % user_id, 0, sku_id)  # 去重
        pl.lpush('history_%s' % user_id, sku_id)  # 重开头添加
        pl.ltrim('history_%s' % user_id, 0, 4)  # 截取前5个
        pl.execute()
        return validated_data


class UserGetBrowseHistoriesSerializers(serializers.ModelSerializer):
    """用户查看浏览记录"""

    class Meta:
        model = SKU
        fields = '__all__'




