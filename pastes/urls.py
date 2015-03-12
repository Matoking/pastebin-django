from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from pastes import views

urlpatterns = patterns('',
    url(r'^submit_paste/', views.submit_paste, name="submit_paste"),
)
