import os

from celery import Celery

# 为celery使用django配置文件进行设置
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 1.创建celery应用
app = Celery('meiduo', backend='redis://localhost:6379/7', broker='redis://localhost:6379/8')

# 2.导入celery配置
app.config_from_object('celery_tasks.config')

# 3.自动注册celery任务
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])
