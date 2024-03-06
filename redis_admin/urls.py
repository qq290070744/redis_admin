"""
URL configuration for redis_admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path
from users.views import LoginViews, LogoutView, ChangeUser, AddUser, UserRegisterView, EditUser
from loginfo.views import OperationInfoEditView, OperationInfoDelView, UserManageView
from monitor.views import (GetKeyView, GetRedisInfo, CheckRedisContent, GetIdView,
                           GetValueView, RedisErrorHtmlView, ClientHtmlView, ClientListView,
                           DelKeyView, EditValueTableView, BgSaveView, AddKeyView, ClearDbView,
                           RedisListView, RedisEditView, RedisAddView, RedisDelView
                           )

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', GetRedisInfo.as_view(), name='index'),
    re_path(r'^check/redis/$', CheckRedisContent.as_view(), name='checkredis'),
    re_path(r'^error/$', RedisErrorHtmlView.as_view(), name='redis_error'),
    re_path(r'^login/$', LoginViews.as_view(), name='login'),
    re_path(r'^logout/$', LogoutView.as_view(), name='logout'),
    re_path(r'^(?P<redis_name>\w+)/db(?P<id>[0-9]+)/$', GetIdView.as_view(), name='getid'),
    re_path(r'^get_key/(?P<redis_name>\w+)/(?P<db_id>[0-9]+)/$', GetKeyView.as_view(), name='getkey'),
    re_path(r'^view/(?P<redis_name>\w+)/(?P<value_db_id>[0-9]+)/(?P<key>.*)/$', GetValueView.as_view(),
            name='getvalue'),
    re_path(r'^client/(?P<client_id>[0-9]+)/$', ClientHtmlView.as_view(), name='client_html'),
    re_path(r'^client_list/$', ClientListView.as_view(), name='client_list'),
    re_path(r'^del/key/$', DelKeyView.as_view(), name='del_key'),
    re_path(r'^edit/(?P<redis_name>\w+)/db(?P<edit_db_id>[0-9]+)/$', EditValueTableView.as_view(),
            name='edit_key'),
    re_path(r'^bgsave/(?P<redis_id>[0-9]+)/$', BgSaveView.as_view(), name='bg_save'),
    re_path(r'^operation/info/edit/$', OperationInfoEditView.as_view(), name='operation_edit'),
    re_path(r'^operation/info/del/$', OperationInfoDelView.as_view(), name='operation_del'),
    re_path(r'^user/manage/$', UserManageView.as_view(), name='user_manage'),
    re_path(r'^change/user/$', ChangeUser.as_view(), name='change_user'),
    re_path(r'^add/user/$', AddUser.as_view(), name='add_user'),
    re_path(r'^edit/user/$', EditUser.as_view(), name='edit_user'),
    re_path(r'^add/key/(?P<redis_name>\w+)/$', AddKeyView.as_view(), name='add_key'),
    re_path(r'^clear/db$', ClearDbView.as_view(), name='clear_db'),
    re_path(r'^register/$', UserRegisterView.as_view(), name="register"),
    re_path(r'^redis/list/$', RedisListView.as_view(), name="redis_list"),
    re_path(r'^redis/list/edit/$', RedisEditView.as_view(), name="redis_edit"),
    re_path(r'^redis/list/add/$', RedisAddView.as_view(), name="redis_add"),
    re_path(r'^redis/list/del/$', RedisDelView.as_view(), name="redis_del"),
]
