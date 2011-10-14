from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',
    (r'^$', 'main'),
    (r'^forum/(\d+)/$', 'forum'),
    (r'^thread/(\d+)/$', 'thread'),
)

