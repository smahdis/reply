from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.post_list, name='post_list.html'),
    url(r'^$', views.index, name='index'),
    url(r'^question/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
]