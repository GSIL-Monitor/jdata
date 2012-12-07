#_*_coding:utf-8 _*_
#!/bin/env python

from jdata.core.dbdata import Data
from jdata.djutils.views import project_dir,simplejson
from jdata.djutils.exceptions import URLParameterError,ObjectNotFound,ObjectConfigError,ObjectConfigTestError,ObjectInitError
import time
import os,imp,urllib2
from jdata.app.models import conf as ObjectConfig



def QueryDict(path):
    if path.find('?')>0:
        path = path[path.find('?')+1:]
    rst = {}
    for kv in path.split('&'):
        try:
            k,v = kv.split('=')
            rst[k]=v
        except:
            rst[kv]=''
    return rst



class DataModel(object):
    def __init__(self,objectname=None,path=None, config = {}):
        self.objectname=objectname
        if not self.objectname:
            if path:
                self.objectname=self.get_objectname_by_path(path)
            elif config:
                self.obj = config
            else:
                raise ObjectInitError('parameter objectname | path | config  is required!')
        if not config:
            self._get_config()
        try:
            self._check_config()
        except Exception as e:
            raise ObjectConfigError('object `'+str(self.objectname)+'` configuration error:   '+str(e))
        self._auto_gen_config()
        self.Data = Data(self.objectname, self.DB, self.FIELDS_ALIAS, self.METADB)

    def check_new_config(self):
        testtable = 'jdata_config_test_table'

        try:
            self.Data.createtable(testtable)
            self.Data.droptable(testtable)
            #self.Data.query('drop table '+testtable,iscache=False, tablename = testtable)
        except Exception as e:
            raise ObjectConfigTestError('object `%s` configuration test : Create Table Error ! %s' %(self.objectname, str(e)))
        try:
            self.Data.createtable(testtable)
            self.Data.query('select * from '+testtable, iscache=False, tablename = testtable)
            self.Data.droptable(testtable)
            #self.Data.query('drop table '+testtable, iscache=False, tablename = testtable)
        except:
            raise ObjectConfigTestError('object `'+self.objectname+'` configuration test  error: Replication Lag ? ')
        
            
    def _get_config(self):
        #os.chdir(project_dir)
        try:_o = ObjectConfig.objects.get(key = self.objectname)
        except:raise ObjectNotFound('object `'+self.objectname+'` not found.')
        self.obj = simplejson.loads(_o.value)
    
    def _check_config(self):
        self.objectname = self.obj['KEY']
        self.FIELDS_DISPNAME = {}
        self.DB = self.obj['DB']
        _s = self.DB['mysql']['table_split_idx']
        self.DB['mysql']['table_split_idx'] = int(_s)
        #mysqlconfig = self.DB['mysql']['writerurl']
        _METADB = self.obj['METADB']
        self.METADB = []
        for i in _METADB:
            self.METADB.append((i['name'],i['lambda'],i['alias']))
            self.FIELDS_DISPNAME[i['name']] = i['alias']
        _FIELDS_ALIAS = self.obj['FIELDS_ALIAS']
        self.FIELDS_ALIAS={}
        for i in _FIELDS_ALIAS:
            self.FIELDS_ALIAS[i['name']] = (i['lambda'],i['alias'])
            self.FIELDS_DISPNAME[i['name']] = i['alias']
        self.NAME = self.obj['NAME']
        

    def _auto_gen_config(self):
        #self.URL_ALIAS = self.obj.get('URL_ALIAS',{'s':'starttime','e':'endtime'})
        self.SHOW_IN_QUERY = self.obj.get('SHOW_IN_QUERY',False)
        _ALLOWIPS = self.obj.get('ALLOWIPS',[])
        self.ALLOWIPS = [i['ip'] for i in _ALLOWIPS]

        #generel METADB_CHART
        str_fields =  [ i[0] for i in  list(self.METADB) if 'char' in i[1]]
        str_fields.remove(self.FIELDS_ALIAS['timeline'][0])
        int_fields = self.FIELDS_ALIAS.keys() + [ i[0] for i in  list(self.METADB) if ('int' in i[1] or 'float' in i[1])]
        int_fields.remove('timeline') 
        self.METADB_CHART = {}
        for i in str_fields:
            self.METADB_CHART[i] = {'p':i,'name':(self.FIELDS_DISPNAME.get(i) or i),'pageby':True,'filter':True,'fields':False}
        for i in int_fields:
            self.METADB_CHART[i] = {'p':i,'name':(self.FIELDS_DISPNAME.get(i) or i),'pageby':False,'filter':False,'fields':True}
        
        
        """
        self.DB = hasattr(obj,'DB') and getattr(obj,'DB') or obj['DB']
        self.METADB = hasattr(obj,'METADB') and getattr(obj,'METADB') or obj['METADB']
        try:    self.URL_ALIAS = hasattr(obj,'URL_ALIAS') and getattr(obj,'URL_ALIAS') or obj['URL_ALIAS']
        except: self.URL_ALIAS = {'s':'starttime','e':'endtime'}
        self.FIELDS_ALIAS = hasattr(obj,'FIELDS_ALIAS') and getattr(obj,'FIELDS_ALIAS') or obj['FIELDS_ALIAS']
        self.Data = Data(self.DB,'mysql',self.FIELDS_ALIAS,self.METADB)
        _FIELDS_NAME = {}
        for i in self.METADB:
            try:_FIELDS_NAME[i[0]] = i[2]
            except:pass
        _FIELDS_NAME.update(dict([(ii[0],ii[1][1]) for ii in self.FIELDS_ALIAS.items()]))

        str_fields =  [ i[0] for i in  list(self.METADB) if 'char' in i[1]]
        int_fields = self.FIELDS_ALIAS.keys()
        int_fields.remove('timeline')
        result = {}
        for i in str_fields:
            result[i] = {'p':i,'name':(_FIELDS_NAME.get(i) or i),'pageby':True,'filter':True,'fields':False}
        for i in int_fields:
            result[i] = {'p':i,'name':(_FIELDS_NAME.get(i) or i),'pageby':False,'filter':False,'fields':True}
        #print 're',result
        _METADB_CHART = result
        #_METADB_CHART[obj.FIELDS_ALIAS['timeline'][0]]['filter'] = False  
        try:
            del _METADB_CHART[obj.FIELDS_ALIAS['timeline'][0]] 
        except:
            pass
        try:
            del _METADB_CHART['ptime']
        except:
            pass

        METADB_CHART_ = hasattr(obj,'METADB_CHART') and getattr(obj,"METADB_CHART",{}) or obj['METADB_CHART']
        _METADB_CHART.update(METADB_CHART_.copy())
        try:self.NAME = obj.NAME
        except:self.NAME = objectname
        try:self.METADB_CHART = _METADB_CHART
        except:self.METADB_CHART = {}
        try:self.SHOW_IN_QUERY = obj.SHOW_IN_QUERY
        except:self.SHOW_IN_QUERY = True
        try:self.TRUSTED_IPS = obj.TRUSTED_IPS.values()
        except: self.TRUSTED_IPS = []
        try:
            self.DB['mysql']['writer'] = self.DB['mysql']['writerurl']
            self.DB['mysql']['reader'] = self.DB['mysql']['readerurl']
        except:
            pass
        self.ALLOWIPS = obj.get('ALLOWIPS') or []
        """
        
    def get_objectname_by_path(self,path):
        items=QueryDict(path).items()
        for i in items:
            if i[0] == '_o':
                return i[1]
        raise URLParameterError('parameter  `_o` is required.') 

    
        
    def get_query_dict(self,path):
        path = urllib2.unquote(path)
        items=QueryDict(path).items()
        query_dict={}
        query_dict['_pageby']=[]
        query_dict['_fields']=[]
        query_dict['_filters']=[]
        for i in items:
            if i[0] == '_o' :
                query_dict['_o']=i[1]
        for i in items:
            k = i[0][i[0].find('?')+1:]
            if k =='_pageby':
                if len(i[1])>0:
                    for f in i[1].split(','):
                        query_dict['_pageby'].append(f)
            elif k =='_fields':
                for f in i[1].split(','):
                    query_dict['_fields'].append(f)
            elif k.find('_') == 0:
                query_dict[k] = i[1]
            elif k == '':
                continue
            else:
                if i[1]=='':
                    query_dict['_filters'].append(k)
                elif i[1].find('%')>=0:
                    query_dict['_filters'].append(k+' like "'+i[1]+'"')
                else:
                    query_dict['_filters'].append(k+'="'+i[1]+'"')
        if query_dict.has_key('_nourlcheck'):
            return query_dict
        if not query_dict.has_key('_o'):
            raise URLParameterError('parameter  `_o` is required.')
        for i in query_dict['_fields']:
            keys = self.FIELDS_ALIAS.keys() + self.Data.cols
            if i not in keys:
                raise URLParameterError('Unknown field `'+i+'` in `_fields` , expecting one of: "'+', '.join(keys)+'"')
        for i in query_dict['_filters'] + query_dict['_pageby']:
            i = i.split()[0].split('=')[0]
            if not (i in self.Data.cols):
                raise URLParameterError('Unknown field `'+i+'` , expecting one of: "'+', '.join(self.Data.cols)+'"')
        tstep = query_dict.get('_tstep',5)
        try:
            if int(tstep) > 60:
                raise URLParameterError('`_tstep` must less than 60 minute ,default is 5(min), current value is %s' %tstep)
        except ValueError:
            raise URLParameterError('The value of parameter `_tstep` must integer')
        return query_dict
