#_*_coding:utf-8 _*_
# Create your views here.
from django.http import Http404, HttpResponse,HttpResponseRedirect
from django.utils import simplejson
from settings import PROJECT_DIR as project_dir
from django.core.cache import cache as sqlcache
import decimal
import datetime



def json_encode_decimal(obj):
	if isinstance(obj, decimal.Decimal):
		return str(obj)
	if isinstance(obj, datetime.datetime):
		return str(obj)
    
	raise TypeError(repr(obj) + " is not JSON serializable")


def return_http_json(rst):
	r = HttpResponse()
	r.write(simplejson.dumps(rst,default=json_encode_decimal))
	return r
	
