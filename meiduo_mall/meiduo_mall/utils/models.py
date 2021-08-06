from django.db import models


class BaseModel(models.Model):
    """模型添加时间字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 抽象模型类，数据库迁移不会添加本表
