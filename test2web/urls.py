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
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from test2web.page import *

urlpatterns = [
    url(r'^warning/$', warning_page, name='warning'),
    url(r'^stat/$', stat_page, name='stat'),
    url(r'^dict/$', dict_page, name='dict'),
    # url(r'^init/$', init, name='init'),
    url(r'^add_warning/$', add_warning, name='add_warning'),
    url(r'^search_warning/$', search_warning, name='search_warning'),
    url(r'^detail/(.*)/(.*)/(.*)/(.*)/$', warning_detail, name='warning_detail'),
    url(r'^$', stat_page, name='stat'),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.UPLOAD_URL, document_root=settings.UPLOAD_ROOT)
