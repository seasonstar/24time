from django.conf.urls.defaults import *

urlpatterns = patterns('cal.views',
    (r"^(\d+)/$", "main"),
    (r"^$", "main"),
    (r'^month/(\d+)/(\d+)/(prev|next/$)', 'month'),
    (r'^month/(\d+)/(\d+)/$', 'month'),
    (r'^month/$', 'month'),
    (r'^day/(\d+)/(\d+)/(\d+)/$',"day"),
)

