from django.contrib import admin
from discuss.models import *

admin.site.register(Discussion)
admin.site.register(UserProfile)
admin.site.register(Article)
admin.site.register(DiscussionState)