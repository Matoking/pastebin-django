from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from pastes import views, admin_views

urlpatterns = patterns('',
    url(r'^(?P<char_id>\w{8})/remove/$', views.remove_paste, name="remove_paste"),
    url(r'^(?P<char_id>\w{8})/edit/$', views.edit_paste, name="edit_paste"),
    url(r'^(?P<char_id>\w{8})/report/$', views.report_paste, name="report_paste"),
    
    url(r'^(?P<char_id>\w{8})/history/(?P<page>\d+)/$', views.paste_history, name="paste_history"),
    url(r'^(?P<char_id>\w{8})/history/$', views.paste_history, {"page": 1}, name="paste_history"),
    
    url(r'^change_paste_favorite/$', views.change_paste_favorite, name="change_paste_favorite"),
)