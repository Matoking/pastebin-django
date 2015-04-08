from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from pastes import views

urlpatterns = patterns('',
    url(r'^(?P<char_id>\w{8})/delete', views.delete_paste, name="delete_paste"),
    url(r'^(?P<char_id>\w{8})/edit', views.edit_paste, name="edit_paste"),
    
    url(r'^change_paste_favorite/', views.change_paste_favorite, name="change_paste_favorite"),
)
