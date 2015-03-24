from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from users import views

urlpatterns = patterns('',
    url(r'^register/', views.register_view, name="register"),
    url(r'^login/', views.login_view, name="login"),
    url(r'^logout/', views.logout_view, name="logout"),
    
    url(r'^(?P<username>\w+)/pastes', views.pastes, name="pastes"),
    url(r'^(?P<username>\w+)/favorites', views.favorites, name="favorites"),
    url(r'^(?P<username>\w+)/$', views.profile, name="profile"),
)
