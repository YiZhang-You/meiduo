from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from django_redis import get_redis_connection

from goods.models import SKU

from .models import OrderInfo, OrderGoods


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车数据序列化器"""
    count = serializers.IntegerField(label='商品数量')

    class Meta:
        model = SKU
        fields = ['id', 'name', 'default_image_url', 'price', 'count']


class OrderSettlementSerializer(serializers.Serializer):
    """订单结算序列化"""
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class CommitOrderSerializer(serializers.ModelSerializer):
    """生成订单"""

    class Meta:
        model = OrderInfo
        fields = ['order_id', 'pay_method', 'address']
        read_only_fields = ['order_id']
        extra_kwargs = {
            'address': {'write_only': True},
            'pay_method': {'write_only': True},
        }

    def create(self, validated_data):
        # 获取当前下单用户
        user = self.context['request'].user
        # 生成订单编号
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
        address = validated_data.get('address')
        pay_method = validated_data.get('pay_method')
        status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else \
            OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        # 保存订单基本信息数据 OrderInfo
        with transaction.atomic():  # 1.开启事务
            save_id = transaction.savepoint()  # 2.创建保存点出错了就返回这里
            try:
                orderInfo = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status,
                )
                # 从redis中获取购物车结算商品数据
                redis_conn = get_redis_connection('cart')
                cart_dict_redis = redis_conn.hgetall('cart_%d' % user.id)
                selected_ids = redis_conn.smembers('selected_%d' % user.id)
                # 遍历购物车结算商品：
                for sku_id_bytes in selected_ids:
                    while True:  # 解决并发
                        sku = SKU.objects.get(id=sku_id_bytes)
                        # 判断商品库存是否充足
                        buy_count = int(cart_dict_redis[sku_id_bytes])  # 用户购买的数量
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        if buy_count > origin_stock:
                            raise serializers.ValidationError('库存不足')
                        # 减少商品库存，增加商品销量
                        new_stock = origin_stock - buy_count
                        new_sales = origin_sales + buy_count
                        # sku.stock = new_stock
                        # sku.sales = new_sales
                        # sku.save()
                        # 乐观锁的处理并发操作就是，在购买的时候查询一下数据库库存和销量是不是没有发生变化,没有发生变化就修改。发生修改就返回0进行下一次循环
                        result = SKU.objects.filter(stock=origin_stock, sales=origin_sales).update(stock=new_stock,
                                                                                                   sales=new_sales)
                        if result == 0:
                            continue
                        spu = sku.goods
                        spu.sales = spu.sales + buy_count
                        spu.save()
                        # 保存订单商品数据
                        OrderGoods.objects.create(
                            order=orderInfo,
                            sku=sku,
                            count=buy_count,
                            price=sku.price,
                        )
                        orderInfo.total_count += buy_count
                        orderInfo.total_amount += (sku.price * buy_count)
                        break
                orderInfo.total_amount += orderInfo.freight
                orderInfo.save()
            except Exception:
                transaction.savepoint_rollback(save_id)  # 3.暴力回滚
                raise serializers.ValidationError('库存不足')
            else:
                transaction.savepoint_commit(save_id)  # 4.没有问题就提交事务

        # 在redis购物车中删除已计算商品数据
        pl = redis_conn.pipeline()
        pl.hdel('cart_%d' % user.id, *selected_ids)
        pl.srem('selected_%d' % user.id, *selected_ids)
        pl.execute()

        return orderInfo
