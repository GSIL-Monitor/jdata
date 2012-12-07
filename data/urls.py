from django.conf.urls.defaults import *

from jdata.data import views

urlpatterns = patterns('',
        # The register view:
	(r'^q/?$',views.q),
        )
