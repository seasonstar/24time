from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^poll/', include('poll.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^blog/', include('blog.urls')),
    (r'^photo/', include('photo.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)
