import xadmin
from xadmin import views

from . import models


class OrderInfoAdmin(object):
    model_icon = 'fa fa-gift'
    list_display = ['order_id', 'user', 'address']
    data_charts = {
        "order_amount": {'title': '订单金额', "x-field": "create_time", "y-field": ('total_amount',),
                         "order": ('create_time',)},
        "order_count": {'title': '订单量', "x-field": "create_time", "y-field": ('total_count',),
                        "order": ('create_time',)},
    }


xadmin.site.register(models.OrderInfo, OrderInfoAdmin)
