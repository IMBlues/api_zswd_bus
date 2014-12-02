#! -*- coding:utf-8 -*-
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'zq_bus.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += patterns('bus.views',

    url(r'update_bus_info/$', 'update_bus_position'),
    url(r'get_bus_info/$', 'get_bus_info'),
    url(r'get_user_position/$', 'return_user_position'),

)
