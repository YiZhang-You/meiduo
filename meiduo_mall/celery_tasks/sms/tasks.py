from django.conf import settings
import logging
from rest_framework.response import Response
from .Tencent.sms import send_sms_single
from celery_tasks.main import app

# 发送短信的异步任务
logger = logging.getLogger("django")


# 装饰器将send_sms_code装饰为异步任务,并设置别名
@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信异步任务
    :param mobile: ⼿机号
    :param sms_code: 短信验证码
    :return: None
    """
    try:
        result = send_sms_single(mobile, settings.TENCENT_SMS_TEMPLATE.get('register'), [sms_code, ])
        print(result)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
        return Response({'massage':"发送验证码短信[异常]"})
    else:
        if result['result'] == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        elif result['result'] == 1025:
            raise Exception({'massage': "手机号日频率限制"})
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            return Response({'massage': "发送验证码短信[失败]"})

