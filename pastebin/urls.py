from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

from pastes import views as paste_views
from home import views as home_views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pastebin.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Django's in-built admin interface
    url(r'^admin/', include(admin.site.urls)),
    
    # Home page
    #url(r'^$', TemplateView.as_view(template_name='homepage.html'), name="homepage"),
    url(r'^$', include("home.urls", namespace="home")),
    
    url(r'^latest_pastes/(?P<page>\d+)/$', home_views.latest_pastes, name="latest_pastes"),
    url(r'^latest_pastes/$', home_views.latest_pastes, name="latest_pastes"),
    
    url(r'^faq/$', home_views.faq, name="faq"),
    
    url(r'^random/$', home_views.random_paste, name="random_paste"),
    
    url(r'^pastes/', include("pastes.urls", namespace="pastes")),
    url(r'^users/', include("users.urls", namespace="users")),
    url(r'^comments/', include("comments.urls", namespace="comments")),
    
    url(r'^(?P<char_id>\w{8})/raw/(?P<version>\d+)/$', paste_views.show_paste, {"raw": True}, name="raw_paste"),
    url(r'^(?P<char_id>\w{8})/raw/$', paste_views.show_paste, {"raw": True}, name="raw_paste"),
    
    url(r'^(?P<char_id>\w{8})/download/(?P<version>\d+)/$', paste_views.show_paste, {"download": True}, name="download_paste"),
    url(r'^(?P<char_id>\w{8})/download/$', paste_views.show_paste, {"download": True}, name="download_paste"),
    
    url(r'^(?P<char_id>\w{8})/(?P<version>\d+)/$', paste_views.show_paste, name="show_paste"),
    url(r'^(?P<char_id>\w{8})/$', paste_views.show_paste, name="show_paste"),
)
