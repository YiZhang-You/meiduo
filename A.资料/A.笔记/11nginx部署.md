django仅在调试模式下（DEBUG=True）能对外提供静态文件。

当DEBUG=False工作在生产模型时(上线时)，django不在对外提供静态文件，需要用Collesctstatic命令并交由其他静态文件服务器来提供。



# 一、静态业务逻辑

### 1.收集项目的静态文件

#### 1.1 创建文件夹 

```
当Django运⾏在⽣产模式时，将不再提供静态⽂件的⽀持，需要将静态⽂件交给静态⽂件服务器。
项⽬中的静态⽂件除了我们使⽤的front_end_pc中之外，django本身还有⾃⼰的静态⽂件，如果rest_framework、xadmin、admin、ckeditor等。我们需要收集这些静态⽂件，集中⼀起放到静态⽂件服务器中。
我们要将收集的静态⽂件放到front_end_pc⽬录下的static⽬录中，所以先创建⽬录static
```

#### 1.2 配置静态⽂件存储⽬录（settings中)

```python
# 配置静态⽂件收集之后存放的⽬录
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc/static')
```

#### 1.3 执⾏收集命令

```
python manage.py collectstatic  # 没有的话就pip下载
```

### 2. 部署静态文件到nginx服务器

#### 2.1 下载nginx

```
sudo apt-get install nginx  # （有的系统有自带的可以 nginx -v查看一下）
```

#### 2.2 配置nginx服务器

1、打开nginx配置⽂件

```
sudo vim /usr/local/nginx/conf/nginx.conf

# 我的ubantu18是在 /etc里面
```

2、配置server部分

```
user  root;
worker_processes  1;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;
    proxy_connect_timeout 120;
    proxy_read_timeout 120;
    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    # keepalive_timeout  0;
    keepalive_timeout  1000;
    upstream meiduo {
        server 192.168.171.128:8001;  # 此处为uwsgi运行的ip地址和端口号
        # 如果有多台服务器，可以在此处继续添加服务器地址
    }

    #gzip  on;  # 动态后台
    server {
        listen  8000;
        server_name api.meiduo.site;

        location / {
            include uwsgi_params;
            uwsgi_pass meiduo;
        }
     }
    # 以下是静态业务逻辑 前台
    server {
        listen       80;
        server_name  www.meiduo.site;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;
        #location /xadmin {
         #    include uwsgi_params;
          #   uwsgi_pass meiduo;
         #}

         #location /ckeditor {
          #   include uwsgi_params;
           #  uwsgi_pass meiduo;
         #}

         location / {
             root   /home/python/Desktop/front_end_pc;  # 前端位置
             index  index.html index.htm;
         }
}

```

3、开启nginx服务器静态域名

```
nginx :第一次开启
nginx -s reload :重启
nginx -s stop ：关闭
```

### 3. 配置nginx服务器静态域名

```
# 127.0.0.1       www.meiduo.site
# 127.0.0.1       api.meiduo.site
# 127.0.0.1     image.meiduo.site

192.168.171.128         www.meiduo.site
192.168.171.128         api.meiduo.site
192.168.171.128         image.meiduo.site
```

### 4.测试

```
http://www.meiduo.site
```



## 前端nginx配置

nginx：专门提供静态文件的访问



先收集项目中的静态文件，放到前端的文件中



我的这个nginx默认在/etc下，使用一定要注意操作



# 二、动态业务逻辑

### 1.准备⽣产环境的配置⽂件

### uwsgi

1、把dev.py中的代码，前面复制一份到prod.py中

2、改DEBUG = False

3、给白名单添加域名 

​	ALLOWED_HOSTS = 【】

​	CORS_ORIGIN_WHITELIST = 【】

### 2.定wsgi.py启动配置⽂件为prod.py

```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.prod")
application = get_wsgi_application()
```

### 3.安装uwsgi服务器程序

```
pip install uwsgi  # 提示：django的程序通常使⽤uwsgi服务器来运⾏
```

### 4. 创建uwsgin服务器启动文件

创建一个uwsgin.ini文件

```python
[uwsgi]
#使用nginx连接时使用，Django程序所在服务器地址
socket=192.168.171.128:8001
#直接做web服务器使用，Django程序所在服务器地址
# http=192.168.199.133:8001
#项目目录
chdir=/home/YLG/Project/meiduo/meiduo_mall
#项目中wsgi.py文件的目录，相对于项目目录
wsgi-file=meiduo_mall/wsgi.py
# 进程数
processes=4
# 线程数
threads=2
# uwsgi服务器的角色
master=True
# 存放进程编号的文件
pidfile=uwsgi.pid
# 日志文件，因为uwsgi可以脱离终端在后台运行，日志看不见。我们以前的runserver是依赖终端的
daemonize=uwsgi.log
# 指定依赖的虚拟环境
virtualenv=/root/.virtualenvs/meiduo
```

### 5.uwsgin服务器命令

```
启动 uwsgi --ini uwsgi.ini
停⽌ uwsgi --stop uwsgi.pid
或者 kill
```

### 6.配置nginx服务器分发动态业务逻辑

- nginx.conf ，我的这个文件在etc下

- 内容

  ```
   upstream meiduo {
          server 192.168.171.128:8001;  # 此处为uwsgi运行的ip地址和端口号
          # 如果有多台服务器，可以在此处继续添加服务器地址
      }
  
      #gzip  on;
      server {
          listen  8000;
          server_name api.meiduo.site;
  
          location / {
              include uwsgi_params;
              uwsgi_pass meiduo;
          }
       }
  ```

- 重启nginx

  ```
  第⼀次开启 sudo /usr/local/nginx/sbin/nginx
  重启 sudo /usr/local/nginx/sbin/nginx -s reload
  关闭 sudo /usr/local/nginx/sbin/nginx -s stop
  
  fnngj@ubuntu:~$ /etc/init.d/nginx start  #启动
  fnngj@ubuntu:~$ /etc/init.d/nginx stop  #关闭
  fnngj@ubuntu:~$ /etc/init.d/nginx restart  #重启
  ```

- 配置nginx服务器静态域名

  ```
  # 127.0.0.1       www.meiduo.site
  # 127.0.0.1       api.meiduo.site
  # 127.0.0.1     image.meiduo.site
  
  192.168.171.128         www.meiduo.site
  192.168.171.128         api.meiduo.site
  192.168.171.128         image.meiduo.site
  ```

- 测试

  ```
  http://www.meiduo.site/list.html?cat=115
  既有静态的，也有动态的
  ```

  

### nginx



