import re

from rest_framework import serializers
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from .models import User, Address
from celery_tasks.email.tasks import send_verify_email


class UsersSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label="确认密码", write_only=True)
    sms_code = serializers.CharField(label="验证码", write_only=True)
    allow = serializers.CharField(label="是否同意协议", write_only=True)
    token = serializers.CharField(label='登录状态', read_only=True)  # 保存在redis

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的⽤户名',
                    'max_length': '仅允许5-20个字符的⽤户名'
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码'
                }
            }
        }

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}', value):
            raise serializers.ValidationError("手机号格式错误")
        return value

    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError("你没有同意用户协议")
        return value

    def validate(self, attrs):
        print(attrs)
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("二次输入不一致")
        # sms_code 校验验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = attrs['mobile']
        get_redis_code = redis_conn.get('sms_%s' % mobile)
        if get_redis_code is None:
            raise serializers.ValidationError("请重新发送短信")
        if attrs['sms_code'] != get_redis_code.decode():
            raise serializers.ValidationError("验证码错误")
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """展示用户信息序列化"""

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


class EmailSerializer(serializers.ModelSerializer):
    """添加邮箱，修改邮箱状态"""

    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                'required': True,  # 必须输入
            }
        }

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email')
        instance.save()
        # ⽣成激活链接, 获取当前用户的信息，拼接成url
        verify_url = instance.generate_email_verify_url()  # 获取用户信息，我们直接把方法写在Modls中，这样就不用写获取用户信息的了
        print(verify_url)
        # 异步发送邮件
        send_verify_email.delay(instance.email, verify_url)  # verify_url认证链接
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """用户地址序列化器"""
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ['user', 'is_deleted', 'create_time', 'update_time']

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return Address.objects.create(**validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """地址标题"""
    class Meta:
        model = Address
        fields = ('title',)
