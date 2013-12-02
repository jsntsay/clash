from django.conf.urls import patterns, include, url

# User class for built-in authentication module
from django.contrib.auth.models import User

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('discuss.urls')),
	url(r'^admin/', include(admin.site.urls)),
)
