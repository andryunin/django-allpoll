from django.conf.urls import patterns, include, url

from allpoll import views

urlpatterns = patterns('',
    url(r'^$', views.poll_list, name='list'),
    url(r'^(?P<poll_id>\d+)$', views.poll_vote, name='vote'),
)
