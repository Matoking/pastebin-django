from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from users import views

urlpatterns = patterns('',
    url(r'^register/', views.register_view, name="register"),
    url(r'^login/', views.login_view, name="login"),
    url(r'^logout/', views.logout_view, name="logout"),
    
    url(r'^(?P<username>\w+)/pastes/(?P<page>\d+)', views.profile, {"tab": "pastes"}, name="pastes"),
    url(r'^(?P<username>\w+)/pastes', views.profile, {"tab": "pastes",
                                                      "page": 1}, name="pastes"),
    
    url(r'^(?P<username>\w+)/favorites/(?P<page>\d+)', views.profile, {"tab": "favorites"}, name="favorites"),
    url(r'^(?P<username>\w+)/favorites', views.profile, {"tab": "favorites",
                                                         "page": 1}, name="favorites"),
    
    url(r'^(?P<username>\w+)/$', views.profile, {"tab": "home"}, name="profile"),
)
