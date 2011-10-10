from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('photo.views',
    (r'^$', 'main'),
    (r'^(\d+)/$', 'album'),
    (r'^image/(\d+)/$', 'image'),
    (r'^(\d+)/(full|thumbnails|edit)/$', 'album'),
    (r'^update/$', 'update'),
    (r'^search/$', 'search'),

)
