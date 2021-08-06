from random import randint

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django_redis import get_redis_connection

from celery_tasks.sms import tasks


class SMSCodeView(APIView):
    """获取短信验证码"""

    def get(self, request, mobile):
        # 1. 创建连接到redis的对象
        # 2. 先判断用户在60s内是否重复发送短信
        # 3. 如果send_flag有值, 说明60s内重复发发送短信
        # 4. 生成短信验证码
        # 5. 把验证码存储到redis数据库 有效期300秒
        # 6. 存储一个标记，表示此手机号发送过短信，有效期60S
        # 7. 利用腾讯云发送短信验证码
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            return Response({'massage': '频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)
        sms_code = "%06d" % randint(0, 999999)
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, 300, sms_code)
        pl.setex("send_flag_%s" % mobile, 60, 1)
        pl.execute()

        s = tasks.send_sms_code(mobile, sms_code)
        print(s)
        return Response({'message': 'ok!'})
