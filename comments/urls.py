from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from comments import views

urlpatterns = patterns('',
    url(r'^get_comments/', views.get_comments, name="get_comments"),
    url(r'^add_comment/', views.add_comment, name="add_comment"),
    
    url(r'^edit_comment/', views.edit_comment, name="edit_comment"),
)
