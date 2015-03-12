from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pastesite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Django's in-built admin interface
    url(r'^admin/', include(admin.site.urls)),
    
    # Home page
    #url(r'^$', TemplateView.as_view(template_name='homepage.html'), name="homepage"),
    url(r'^$', include("home.urls", namespace="home")),
    url(r'^pastes/', include("pastes.urls", namespace="pastes")),
)
