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
u"""
配置文件的老版本和新版本的兼容
"""
class Qdict(dict):

    def __getattr__(self,key):
        return self.__getitem__(key)


class Qconf(object):

    def __init__(self,objname):
        self.from_ = None
        self.objectname = objname
        self.keys = ["METADB_CHART","DB","METADB","NAME","FIELDS_ALIAS","SHOW_IN_QUERY","SHOW_QUERY_LABLE","PRIMART_KEY","ALLOWIPS"]   
        self.conf = {}

    def file2obj(self,obj):
        u"""
        早前的file配置文件转为标准的配置文件
        """
        for key in self.keys:
            self.conf[key] = getattr(obj,key,None) 
        if not self.conf['METADB_CHART']:
            self.conf['METADB_CHART']={}
        return self.conf

    def db2obj(self,objname):
        u"""
        通过web界面保存的配置文件转换为文件对象
        FiELDS_ALIA,DB需要转换
        """
        from json import loads
        from app.models import conf as Qconf
        try:
            o_ =  Qconf.objects.get(key=objname)
            obj = loads(o_.value)
            print objname
            print o_.value
            print ':'*100
            print obj
            print ':'*100
        except:
            raise
        self.conf = obj
        self.conf['FIELDS_ALIAS'] = self.conf.get('FIELDS_ALIAS') or []
        self.conf['FIELDS_ALIAS_'] = {}
        if type(self.conf['FIELDS_ALIAS'])==list:
            for i in self.conf['FIELDS_ALIAS']:
                self.conf['FIELDS_ALIAS_'][i['name']]= (i['lambda'],i['alias'])
            self.conf['FIELDS_ALIAS'] = self.conf['FIELDS_ALIAS_'] 
        self.conf['METADB'] = self.conf.get('METADB') or []
        self.conf['METADB_'] = []
        if type(self.conf['METADB'])==list and type(self.conf['METADB'][0])==dict:
            for i in self.conf['METADB']:
                if i['alias'].strip():
                    v_ = (i['name'],i['lambda'],i['alias'])
                    self.conf['METADB_'].append(v_)
                else:
                    v_ = (i['name'],i['lambda'])
                    self.conf['METADB_'].append(v_)
                pass
        self.conf['METADB'] = self.conf['METADB_']
        if  not 'primary key' in str(self.conf['METADB']) :
            self.conf['PRIMART_KEY'] = self.conf['PRIMART_KEY'] or []
            primary_key = ','.join([i['name'] for i in self.conf['PRIMART_KEY'] ])
            self.conf['METADB'].append(('primary key','('+primary_key+')'))
        if not self.conf['METADB'][-1][1].strip().strip(')').strip('('):
            self.conf['METADB'].pop()
        self.conf['URL_ALIAS']={'s':'starttime','e':'endtime',}
        print obj
        self.conf['DB']['mysql']['table_split_idx'] = self.conf['DB']['mysql'].get('table_split_idx') or  self.conf['DB']['table_split_idx']
        self.conf['DB']['mysql']['readerurl'] = self.conf['DB']['mysql'].get('readerurl') or self.conf['DB']['readerurl']
        self.conf['DB']['mysql']['writerurl'] = self.conf['DB']['mysql'].get('writerurl')  or self.conf['DB']['writerurl']
        self.conf['DB']['mysql']['tableprefix'] = self.conf['DB']['mysql'].get('tableprefix') or self.conf['DB']['tableprefix']
        self.conf['ALLOWIPS'] = self.conf.get('ALLOWIPS') or []
        return self.conf


    def get_conf(self):
        from app.models import conf as Qconf
        try:
            obj_ = Qconf.objects.get(key=self.objectname.strip())
            self.from_ = "mysql"
        except:
            import imp
            obj = imp.load_source(self.objectname,'conf/'+self.objectname+'.py')
            self.from_ = "file"
        if self.from_ == "file":
            from json import dumps
            self.file2obj(obj)
            c_ = Qconf(key=self.objectname,value=dumps(self.conf)).save()
        elif self.from_ == "mysql":
            print '-'*100
            self.db2obj(self.objectname)
        try:
            self.conf['DB']['table_split_idx'] = self.conf['DB']['mysql']['table_split_idx'] 
            self.conf['DB']['tableprefix'] = self.conf['DB']['mysql']['tableprefix'] 
        except:
            self.conf['DB']['mysql']['table_split_idx'] = self.conf['DB']['table_split_idx'] 
            self.conf['DB']['mysql']['tableprefix'] = self.conf['DB']['tableprefix'] 
        print self.conf
        print self.from_
        return self.conf
