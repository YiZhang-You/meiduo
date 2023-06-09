from django.db import models


class Area(models.Model):
    """省市区"""
    name = models.CharField(max_length=20, verbose_name="名称")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级⾏政区划')  # related_name不用加set

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '⾏政区划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
