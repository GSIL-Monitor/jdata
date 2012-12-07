

from jdata.djutils.views import HttpResponse,project_dir
import urls
import urllib2

def _text2html(str):
    return str.replace('\n','<br>').replace(' ','&nbsp;').replace('\t','&nbsp;' * 10)



def _show_urls(response,urllist,depth=0):
    if depth == 0:
        response.write('#' * 20 + ' ALL APIs ' + '#' * 20)
    for entry in urllist:
        if entry.regex.pattern in ( '^admin/', '^web/', '^static/(?P<path>.*)$'):
            continue
        l = "   " * depth +' '+ entry.regex.pattern +'\n'
        s = str(3+depth)
        #response.write(_text2html('<div style="font-weight:normal"><h'+s+'>'+l+'</h'+s+'></div>'))
        response.write(_text2html('<h'+s+'>'+l+'</h'+s+'>'))
        if hasattr(entry, 'url_patterns'):
            _show_urls(response,entry.url_patterns, depth + 1)
        try:doc = entry.callback.func_doc
        except AttributeError :doc = ''
        if not doc: 
            doc = ''
        else:
            doc = '  >>> ' + doc
        l = "   " * depth +' ' + doc +'\n'
        response.write(_text2html(l))
        



def index(request):
    """
    The manual of Jdata
    e.g.  http:/jdata.qiyi.domain/
    """
    r = HttpResponse()
    f = open(project_dir+'/README','rb')
    r.write('<link rel="stylesheet" type="text/css" media="all" href="http://static.qiyi.com/css/common/hudong2_css/common.css?v=42727" />')
    r.write(f.read().replace('\n','<br>'))
    _show_urls(r,urls.urlpatterns)
    return r


