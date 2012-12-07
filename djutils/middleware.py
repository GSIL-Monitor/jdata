#_*_coding:utf-8 _*_

from jdata.djutils.exceptions import BaseError

class JdataMiddleware(object):
    def process_exception(self, request, e):
        if isinstance(e,BaseError):
            return e.to_django_response()
        else:
            pass
        
        
