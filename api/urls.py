from django.conf.urls.defaults import *

from jdata.api import views,upload

urlpatterns = patterns('',
        # The register view:
	(r'^setting',views.setting),
	(r'^getquerydict',views.getquerydict),
	(r'^uploadresultfile',upload.upload_result_file),
	(r'^gettables',views.gettables),
	(r'^droptables',views.droptables),
        )
