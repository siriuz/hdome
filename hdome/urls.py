from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hdome.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'hdome.views.home', name='home'),
    url(r'^pepsite/', include('pepsite.urls', namespace = 'pepsite' )),
    url(r'^admin/', include(admin.site.urls)),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'hdome.views.logout_page' ),
    url(r'^admin/', include(admin.site.urls)),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^login2/$', 'hdome.views.my_view'),
    (r'^logout/$', 'hdome.views.logout_page' ),
)
