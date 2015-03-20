from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from users import views

urlpatterns = patterns('',
    url(r'^register/', views.register, name="register"),
    url(r'^login/', views.login, name="login"),
)
