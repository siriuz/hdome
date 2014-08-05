from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hdome.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'hdome.views.home', name='home'),
    url(r'^pepsite/', include('pepsite.urls', namespace = 'pepsite' )),
    url(r'^news/', include('news.urls', namespace = 'news' )),
    url(r'^login/$', 'django.contrib.auth.views.login', name = 'login'),
    url(r'^logout/$', 'hdome.views.logout_page', name='logout' ),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^publications/$', 'hdome.views.publications', name='publications'),
    #url(r'^news/$', 'hdome.views.news', name='news'),
    url(r'^sponsors/$', 'hdome.views.sponsors', name='sponsors'),
    url(r'^contact/$', 'hdome.views.contact', name='contact'),
    url(r'^about/$', 'hdome.views.about', name='about'),
    url(r'^banner/$', 'hdome.views.banner', name='banner'),
)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
