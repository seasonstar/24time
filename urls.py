from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^poll/', include('poll.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^blog/', include('blog.urls')),
)
