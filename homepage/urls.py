from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^question/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^register/$', views.register, name='register'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    url(r'^ajax/validate_phone_number/$', views.validate_phone_number, name='validate_phone_number'),
    url(r'^ajax/vote/$', views.vote, name='vote'),
    url(r'^ajax/set_profile/$', views.set_profile, name='set_profile'),
    url(r'^ajax/answer_question/$', views.answer_question, name='answer_question'),
    # url(r'^ajax/downvote/$', views.validate_phone_number, name='validate_phone_number'),
]