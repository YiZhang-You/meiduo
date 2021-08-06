# xadmin

```python
使用教程：https://blog.csdn.net/bocai_xiaodaidai/article/details/94395604?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522162650215716780274162407%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=162650215716780274162407&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_v2~rank_v29-1-94395604.pc_search_result_cache&utm_term=xadmin&spm=1018.2226.3001.4187
```



1.介绍

xadmin就Django的第三方扩展，可使Django的admin站点更方便。





## 1.  安装

通过如下命令安装xadmin的最新版

```shell
pip install https://github.com/sshwsfc/xadmin/tarball/master
```

在配置文件中注册如下应用

```python
INSTALLED_APPS = [
    ...
    'xadmin',
    'crispy_forms',
    'reversion',
    ...
]
```

xadmin有建立自己的数据库模型类，需要进行数据库迁移

```shell
python manage.py makemigrations
python manage.py migrate
```

在总路由中添加xadmin的路由信息

```python
import xadmin

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'xadmin/', include(xadmin.site.urls)),
    ...
]
```

## 2.  使用

- xadmin不再使用Django的admin.py，而是需要编写代码在adminx.py文件中。
- xadmin的站点管理类不用继承`admin.ModelAdmin`，而是直接继承`object`即可。

在goods应用中创建adminx.py文件。

#### 站点的全局配置

```python
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
    site_title = "美多商城运营管理系统"  # 设置站点标题
    site_footer = "美多商城集团有限公司"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠

xadmin.site.register(views.CommAdminView, GlobalSettings)
```

可以直接在http://127.0.0.1:8000/xadmin/查看后台

## 3 参数列表

#### 1. model_icon：显示SKU这张表

```python
import xadmin
from xadmin import views

from . import models

class SKUAdmin(object):
    model_icon = 'fa fa-gift'

xadmin.site.register(models.SKU, SKUAdmin)
```

#### 2.list_display：显示表中的那些字段

```python
list_display = ['id', 'name', 'price', 'stock', 'sales', 'comments']
```

#### 3.search_fields：用那些字段搜索

```python
search_fields = ['id', 'name']
```

#### 4.list_filter：用哪个字段过滤

```python
list_filter = ['category']
```

#### 5.list_editable：设置那些字段可以直接在form表单中修改

```python
list_editable = ['price', 'stock']
```

#### 6.show_detail_fields：查询表单的详细信息

```python
show_detail_fields = ['name']
```

#### 7.show_bookmarks：添加书签

```python
show_bookmarks = True
```

#### 8. list_export：设置导出的格式

```python
 list_export = ['xls', 'csv', 'xml']
```

#### 9.refresh_times：多长时间刷新

```python
refresh_times = [3, 5]  # 可选以支持按多长时间(秒)刷新页面
```

#### 10.data_charts：图表

```python
data_charts = {
    "order_amount": {'title': '订单金额', "x-field": "create_time", "y-field": ('total_amount',),
                     "order": ('create_time',)},
    "order_count": {'title': '订单量', "x-field": "create_time", "y-field": ('total_count',),
                    "order": ('create_time',)},
}
```

## 4.站点保存对象数据方法重写

在Django的原生admin站点中，如果想要在站点保存或删除数据时，补充自定义行为，可以重写如下方法：

- `save_model(self, request, obj, form, change)`
- `delete_model(self, request, obj)`

而在xadmin中，需要重写如下方法：

- `save_models(self)`
- `delete_model(self)`

在方法中，如果需要用到当前处理的模型类对象，需要通过`self.obj`来获取，如

```python
class SKUSpecificationAdmin(object):
    def save_models(self):
        # 保存数据对象
        obj = self.new_obj
        obj.save()

        # 补充自定义行为
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self):
        # 删除数据对象
        obj = self.obj
        sku_id = obj.sku.id
        obj.delete()

        # 补充自定义行为
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)
```

## 自定义用户管理

xadmin会自动为admin站点添加用户User的管理配置

xadmin使用xadmin.plugins.auth.UserAdmin来配置

如果需要自定义User配置的话，需要先unregister(User)，在添加自己的User配置并注册

```python
import xadmin
# Register your models here.

from .models import User
from xadmin.plugins import auth


class UserAdmin(auth.UserAdmin):
    list_display = ['id', 'username', 'mobile', 'email', 'date_joined']
    readonly_fields = ['last_login', 'date_joined']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
    style_fields = {'user_permissions': 'm2m_transfer', 'groups': 'm2m_transfer'}

    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.fields = ['username', 'mobile', 'is_staff']

        return super().get_model_form(**kwargs)


xadmin.site.unregister(User)
xadmin.site.register(User, UserAdmin)
```