"""EpidemicProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path as url

from django.contrib import admin
from django.urls import path,include,re_path
from CampusModule import views
from django.views.static import serve
from django.conf import settings
# handler404 = views.page_not_found

#全局路由增加对本地应用路由文件的引用

# 你是要怎么做   点开 http://127.0.0.1:8000/ 直接进入主页面吗
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.page_not_found),
    path('campus/', include("CampusModule.urls")),
    path('users/', include("UserModule.urls")),
    # url(r'^admin/', admin.site.urls),

    # path('users/', views.users),

    # re_path(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}, name='media')

    # test.com   test.com   user_index.html
#               test.com/campus/

]


'''
admin
zhangyou
'''