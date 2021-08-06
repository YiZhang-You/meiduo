from django.utils.datetime_safe import datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from .models import User, Address
from .serializers import UsersSerializer, UserDetailSerializer, EmailSerializer, AddressTitleSerializer, \
    UserAddressSerializer


class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = UsersSerializer


class UsernameCountView(APIView):
    """判断用户是否存在"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count,
        }
        return Response(data)


class MobileCountView(APIView):
    """判断手机号是否存在"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count,
        }
        return Response(data)


class UserDetailView(RetrieveAPIView):
    """展示用户个人信息"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """修改邮箱状态"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    """用户邮箱解密，更改邮箱的校验状态"""

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({"message": "缺少token"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.check_verify_email_token(token)  # ！！！调用类中的静态方法
        if user is None:
            return Response({"message": "无效的token"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({"message": "ok！"})


class AddressViewSet(UpdateModelMixin, GenericViewSet):
    """收货地址的增删改查"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        user = request.user
        count = Address.objects.filter(user=user).count()
        if count > 20:
            raise Response({'message': '收货地址上线'}, status=status.HTTP_400_BAD_REQUEST)
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        addres = self.get_object()
        addres.is_deleted = True
        addres.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializers = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializers.data,
        })

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """修改标题"""
        addres = self.get_object()
        serializer = AddressTitleSerializer(instance=addres, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """设置默认地址"""
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'ok!'}, status=status.HTTP_200_OK)


jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class UserAuthorizeView(ObtainJSONWebToken):
    """自定义账号密码登录视图,实现购物车登录合并"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            # 账号登录时合并购物车
            merge_cart_cookie_to_redis(request, user, response)

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
