"""test2web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from test2web.page import *
from django.contrib import admin

urlpatterns = [
                  url(r'^warning/$', warning_page, name='warning'),
                  url(r'^stat/$', stat_page, name='stat'),
                  url(r'^dict/$', dict_page, name='dict'),
                  url(r'^info/$', info_page, name='info'),
                  url(r'^init/$', init, name='init'),
                  url(r'^warning_detail/(.*)/(.*)/(.*)/(.*)/(.*)/$', warning_detail, name='warning_detail'),
                  url(r'^add_warning/$', add_warning, name='add_warning'),
                  url(r'^search_warning/$', search_warning, name='search_warning'),
                  url(r'^add_info/$', add_info, name='add_info'),
                  url(r'^add_data/$', import_data, name='import_data'),
                  url(r'^daily_view/$', daily_view, name='daily_view'), # 展示
                  url(r'^daily_manage/$', daily_manage, name='daily_manage'), # 展示
                  url(r'^daily_search/$', daily_search, name='daily_search'), # 展示

                  url(r'^daily_edit/(.*)/$', daily_edit, name='daily_edit'),
                  url(r'^daily_save/(.*)/$', daily_save, name='daily_save'),
                  url(r'^daily_confirm/(.*)/$', daily_confirm, name='daily_confirm'),
                  url(r'^daily_unconfirm/(.*)/$', daily_unconfirm, name='daily_unconfirm'),
                  url(r'^daily_detail_img/(.*)/$', daily_detail_img, name='daily_detail_img'),
                  url(r'^admin/', admin.site.urls, name='admin'),
                  url(r'^$', login),
                #   url(r'^$', 'django.contrib.auth.views.login'),
                  url(r'^accounts/login/$', login),
                # url(r'^accounts/login/$', 'django.contrib.auth.views.login'),

                  url(r'^register/$', register),
                  url(r'^login/', login, name='login'),
                  url(r'^logout/$', logout, name='logout'),
              ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.UPLOAD_URL, document_root=settings.UPLOAD_ROOT)

