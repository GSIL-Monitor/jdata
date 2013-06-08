#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Copyright 2011 timger
    
    +Author timger
    +Gtalk&Email yishenggudou@gmail.com
    +Msn yishenggudou@msn.cn
    +Twitter http://twitter.com/yishenggudou  @yishenggudou
    +Weibo http://t.sina.com/zhanghaibo @timger
    @qiyi
'''
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.http import Http404
import settings 
import os
import datetime
import re
from core.datamodel import DataModel
try:
    import json
except:
    from django.utils import simplejson as json
from models import *
from django.shortcuts import render_to_response

def listobject(request):
    confs =  conf.objects.all()
    confs = [{"key":i.key,"value":json.loads(i.value)} for i in confs]
    return render_to_response("listobjects.html",{'confs':confs})

def rest(request,object_):
    path = request.get_full_path()
    object_ = object_.strip()
    if request.method == 'GET':
        try:
            c_ = conf.objects.get(key=object_)    
            value = json.loads(c_.value)
        except:
            value = {}
        if request.GET.get('type') == "json":
            #兼容以前的配置
            try:
                value['DB']['table_split_idx'] = value['DB']['mysql']['table_split_idx'] 
                value['DB']['tableprefix'] = value['DB']['mysql']['tableprefix'] 
            except:
                value['DB']['mysql']['table_split_idx'] = value['DB']['table_split_idx'] 
                value['DB']['mysql']['tableprefix'] = value['DB']['tableprefix'] 
            if type(value['METADB'][0])==list:
                value['METADB'] = map(lambda x:{'name':x[0],"lambda":x[1],'alias':(len(x)>2 and x[2] or x[0])},value['METADB'])
            if type(value['FIELDS_ALIAS'])==dict:
                value['FIELDS_ALIAS'] = [{'name':i[0],'lambda':i[1][0],'alias':i[1][1]} for i in value['FIELDS_ALIAS'].items()]
            value['KEY']=object_ 
            return HttpResponse(json.dumps(value))
        else:
            return render_to_response("index.html")
    if request.method == "POST":
        object_ = object_ or request.POST.get('key') 
        value = json.loads(request.POST.get('data'))
        check_ = DataModel(config=value)
        print 'value',value
        try:
            check_.check_new_config()
        except Exception as e:
            msg = {'code':"200","success":False,'msg':str(e)}
            return HttpResponse(json.dumps(msg))
        try:
            c_ = conf.objects.get(key=object_) 
            value_ = json.loads(c_.value)
            value_.update(value)
            #print value_
            c_.value = json.dumps(value_)
            c_.save()
        except Exception as e:
            #print 'create a conf object'
            #print e
            c_ = conf(key=object_,value=json.dumps(value))
            c_.save()
        msg = {'code':"200","success":True}
        return HttpResponse(json.dumps(msg))

def check_name_existed(request):
    key = request.GET.get('key')
    try:
        conf.objects.get(key=key)
        msg = {"code":"500","success":False,"msg":"错误改对象已经存在"}
    except:
        msg = {"code":"200","success":True,"msg":"ok"}
    return HttpResponse(json.dumps(msg))


from django.views.decorators.cache import cache_page

#@cache_page(60*60*24, key_prefix="papi")
def papi(request,object_):
    path = request.get_full_path()
    object_ = object_.strip()
    if request.method == 'GET':
        import os
        import sys
        import urllib2
        import yaml
        #import json
        from django.utils import simplejson as json
        from django.core import serializers
        import datetime
        from django.core.cache import cache
        key = 'papi_uuuuuuuuu_' + object_
        if cache.get(key) and request.GET.get('cache')!='false':
            print "read from cache",'-'*10
            return HttpResponse(cache.get(key))
        else:
            date_range = datetime.datetime.now() - datetime.timedelta(1)
            day = date_range.strftime('%Y%m%d')
            s = day+'0000'
            e = day+'2359'
            #默认 
            meta_url = "http://jdata.domain/api/setting?_o=" + object_
            basedata = json.loads(urllib2.urlopen(meta_url).read())
            querys = basedata['METADB']
            querys = filter(lambda x:('char' in x[1]) and ('ptime' not in x[0]) and ('datedd' not in x[0]),querys)
            _fields = basedata['FIELDS_ALIAS']
            del _fields['timeline']
            fields = _fields.keys()[0] 
            #fix
            DIR_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
            path=os.path.join(DIR_PATH,'conf',object_+'.yaml')
            if os.path.isfile(path):
                fix = yaml.load(open(path))
            else:
                fix = {'hides':[]}
            query = {}
            for i in range(len(querys)):
                print i
                print querys[i]
                _ = querys[i]
                query[_[0]] = {'name':_[2],'query':_[0],'selecteds':fix.get(_[0],[])}
                url = 'http://jdata.domain/data/q?_o={o}&_tstep=15&_fields={_fields}&_s={s}&_e={e}&_pageby={pageby}&_lines=fields&_dataclean=0'
                url = url.format(o=object_,_fields=fields,s=s,e=e,pageby=_[0])
                print url
                data_base = (urllib2.urlopen(url).read())
                kk = json.loads(data_base)
                query[_[0]]['selecteds'] = set(query[_[0]]['selecteds']) | set([k[1] for k in kk['Data']])
                query[_[0]]['selecteds'] = list(query[_[0]]['selecteds'])
                query[_[0]]['selecteds'] = [jj.replace('<','')  for jj in query[_[0]]['selecteds']]
            for i in fix['hides']:
                if query.get(i):
                    del query[i] 
            apidata = {}
            apidata['query'] = query
            apidata['fields'] = basedata['FIELDS_ALIAS']
            print apidata
            apidata=json.dumps(apidata)
            #apidata=serializers.serialize('json',apidata)
            cache.set(key,apidata)
            return HttpResponse(apidata)
