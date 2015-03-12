from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from home import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
)
