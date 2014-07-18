from django.conf.urls import patterns, include, url

from news import views

urlpatterns = patterns('',
    url(r'^$', views.bulletin, name='bulletin'),
)
