from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',
    (r'^$', 'main'),
    (r'^post/(\d+)/$','post'),
    (r'^add_comment/(\d+)/$', 'add_comment'),
)

