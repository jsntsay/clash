from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'discuss.views.index', name='index'),
	url(r'discuss/(?P<id>\d+)$', 'discuss.views.discuss', name='discuss'),
	url(r'comments/(?P<id>\d+)$', 'discuss.views.comments', name='comments'),
	url(r'articlecheck/(?P<id>\d+)$', 'discuss.views.articlecheck', name='articlecheck'),
	url(r'contextcheck/(?P<id>\d+)$', 'discuss.views.contextcheck', name='contextcheck'),
	url(r'situationalcheck/(?P<id>\d+)$', 'discuss.views.situationalcheck', name='situationalcheck'),
	url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'discuss/login.html'}, name='login') ,
	# Route to logout a user and send them back to the login page
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
	url(r'^photo/(?P<id>\d+)$', 'discuss.views.get_photo', name='photo'),
)
