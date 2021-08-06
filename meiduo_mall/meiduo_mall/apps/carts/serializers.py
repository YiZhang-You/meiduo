from rest_framework import serializers

from goods.models import SKU


class CartSerializers(serializers.Serializer):
    """购物车新增修改的序列化器"""
    sku_id = serializers.IntegerField(label='商品ID', min_value=1)
    count = serializers.IntegerField(label='购买数量')
    selected = serializers.BooleanField(default=True, label="商品勾选状态")

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("商品不存在")
        return value


class SKUCartSerializers(serializers.ModelSerializer):
    """查询购物车序列化"""
    count = serializers.IntegerField(label="购买数量")
    selected = serializers.BooleanField(default=True, label="商品勾选状态")

    class Meta:
        model = SKU
        fields = ['id', 'count', 'selected', 'name', 'price', 'default_image_url']


class CartDeleteSerializer(serializers.Serializer):
    """删除购物车序列化"""
    sku_id = serializers.IntegerField(label='商品ID')

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("商品不存在")
        return value


class CartSelectedAllSerializer(serializers.Serializer):
    """购物车全选"""
    selected = serializers.BooleanField(label='是否勾选')
