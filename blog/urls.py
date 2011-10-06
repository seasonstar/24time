from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',
    (r'^$', 'main'),
    (r'^post/(\d+)/$','post'),
    (r'^add_comment/(\d+)/$', 'add_comment'),
    (r'^month/(\d+)/(\d+)/$', 'month'),
    (r'^delete_comment/(\d+)/$', 'delete_comment'),
    (r'^delete_comment/(\d+)/(\d+)/$', 'delete_comment'),
)

