import xadmin
from xadmin import views

from . import models


class BaseSetting(object):
    """xadmin的基本配置"""
    enable_themes = True  # 开启主题切换功能
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSetting)


class GlobalSettings(object):
    """xadmin的全局配置"""
    site_title = "美多商城-Y大壮"  # 设置站点标题
    site_footer = "美多商城-Y大壮"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠


xadmin.site.register(views.CommAdminView, GlobalSettings)


class SKUAdmin(object):
    model_icon = 'fa fa-gift'
    list_display = ['id', 'name', 'price', 'stock', 'sales', 'comments']
    refresh_times = [3, 5]  # 可选以支持按多长时间(秒)刷新页面
    search_fields = ['id', 'name']
    list_filter = ['category']
    list_editable = ['price', 'stock']
    show_detail_fields = ['name']
    show_bookmarks = True
    list_export = ['xls', 'csv', 'xml']
    data_charts = {
        "stock": {'title': '库存', "x-field": "create_time", "y-field": ('total_amount',),
                         "order": ('create_time',)},
        "sales": {'title': '销量', "x-field": "create_time", "y-field": ('total_count',),
                        "order": ('create_time',)},
    }
class GoodsCategoryAdmin(object):
    model_icon = 'fa fa-gift'


class GoodsChannelAdmin(object):
    model_icon = 'fa fa-gift'


class BrandAdmin(object):
    model_icon = 'fa fa-gift'


class GoodsAdmin(object):
    model_icon = 'fa fa-gift'


class GoodsSpecificationAdmin(object):
    model_icon = 'fa fa-gift'


class SpecificationOptionAdmin(object):
    model_icon = 'fa fa-gift'


class SKUImageAdmin(object):
    model_icon = 'fa fa-gift'


class SKUSpecificationAdmin(object):
    model_icon = 'fa fa-gift'


xadmin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
xadmin.site.register(models.SKUImage, SKUImageAdmin)
xadmin.site.register(models.SpecificationOption, SpecificationOptionAdmin)
xadmin.site.register(models.GoodsSpecification, GoodsSpecificationAdmin)
xadmin.site.register(models.Goods, GoodsAdmin)
xadmin.site.register(models.GoodsChannel, GoodsChannelAdmin)
xadmin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
xadmin.site.register(models.SKU, SKUAdmin)
