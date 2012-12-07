from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template,redirect_to
from django.contrib import admin
admin.autodiscover()
import os
import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import index

urlpatterns = patterns('',
    # Example:
    # (r'^jdata/', include('jdata.foo.urls')),
    (r'^data/', include('jdata.data.urls')),
    (r'^customdata/', include('jdata.customdata.urls')),
    (r'^api/', include('jdata.api.urls')),
    (r'^$', index.index),

     #(r'^admin/', include(admin.site.urls)),
     (r'^web/', include("app.urls")),
     (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': os.path.join(settings.PROJECT_PATH,'static/')}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
