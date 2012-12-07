#_*_coding:utf-8 _*_
import MySQLdb
from MySQLdb import OperationalError,ProgrammingError,Warning
import copy
import time,md5,os,traceback
from threading import Thread,Lock
from dateutil import rrule
from dateutil.parser import parse

from jdata.djutils.exceptions import *
#TableNotExists,URLParameterError,SpecifiedTimeTooShort,TableNotExistsInDMC,TableNameIsRequried,DebugPrint
import re
class Data(object):
    def __init__(self,objectname, db_conf, fields_alias, meta_db):  #tuple 
        self.objectname = objectname
        self.db_conf=db_conf
        if not self.db_conf['mysql'].get('writerurl',''):
            self.dmc = True
            self.tableprefix = self.objectname
        else:
            self.dmc = False
            self.tableprefix = self.db_conf['mysql']['tableprefix']
        self.dmc_master_w = 'jdata/jdata@bjcnc.jdata.w.qiyi.db:6069/jdata'
        self.dmc_master_r = 'jdata/jdata@bjcnc.jdata.r.qiyi.db:6069/jdata'
        #self.dmc_balance_by = 'Load' # 'Round-Robin'
        self.dmc_balance_by = 'Round-Robin' # 'Round-Robin'
        self.fields_alias=fields_alias
        self.meta_db = meta_db
        self.timefield=self.fields_alias['timeline'][0]
        self.multithreadresult = ()
        self.rowsfromdisk = 0
        self.rowsfrommem = 0
        self.multithreadlock=Lock()
        self._ParseMetaDB()

    def _ParseMetaDB(self):
        self.pk = []
        self.cols = []
        for i in self.meta_db:
            #remove the spaces more then 1
            x = ' '.join([j for j in i[0].split(' ') if j])
            if x == 'primary key':
                pk_cols = i[1].replace(')','').replace('(','').split(',')
                allcols = [j[0].strip() for j in self.meta_db]
                self.pk = [(col,allcols.index(col)) for col in pk_cols]
            elif x == 'index':
                pass
            else:
                self.cols.append(x)
        nonpk_cols = list(set(self.cols) - set([i[0] for i in self.pk]))
        self.nonpk = [(col,self.cols.index(col)) for col in nonpk_cols]

    def query_master(self, sql):
        if sql.lower().find('select') == 0:
            c = self._conn(self.dmc_master_r)
            #print 'MR',sql
        else:
            c = self._conn(self.dmc_master_w)
            #print 'MW',sql
        cur = c.cursor()
        cur.execute(sql)
        t = cur.fetchall()
        cur.execute('commit')
        cur.close()
        c.close()
        return t
            
       
    def dmc_find_node(self, readonly, tablename):
        if not tablename:
            raise TableNameIsRequried('DMC `%s`must need a tablename ' %self.objectname)
        sql = 'select c.writer,c.reader from jdata_dmc_tables t,jdata_dmc_cluster c \
                where t.oname = "%s" and t.tname = "%s" and t.cid = c.cid' %(self.objectname, tablename)
        rst = self.query_master(sql)
        if len(rst) == 0:
            raise TableNotExistsInDMC('%s %s' %(self.objectname, tablename))
        writer,reader = rst[0]
        if readonly:
            return reader
        else:
            return writer
    
    def dmc_roundrobin_next_cid(self):
        sql = 'select cid from jdata_dmc_tables where oname = "%s" order by created desc limit 1' %self.objectname
        try:
            lastcid = self.query_master(sql)[0][0]
        except IndexError:
            lastcid = 0
        sql = 'select cid from jdata_dmc_cluster where cid > %s order by cid limit 1' %lastcid
        try:
            nextcid = self.query_master(sql)[0][0]
        except IndexError:
            s = 'select cid from jdata_dmc_cluster order by cid limit 1'
            nextcid = self.query_master(s)[0][0]
        return nextcid

    def dmc_add_newtable(self, tablename):
        if self.dmc_balance_by == 'Load':
            sql = 'insert into jdata_dmc_tables(oname, tname, cid) \
            select "%s","%s",cid from jdata_dmc_cluster c \
            order by c.load limit 1' %(self.objectname, tablename)
        #elif self.dmc_balance_by  == 'Round-Robin':
        else:
            sql = 'insert into jdata_dmc_tables(oname, tname, cid) \
                values("%s","%s",%s)' %(self.objectname, tablename, self.dmc_roundrobin_next_cid())
        self.query_master(sql)
       
    def dmc_remove_table(self, tablename):
        sql = 'delete from jdata_dmc_tables where oname ="%s" and tname = "%s"' %(self.objectname, tablename)
        self.query_master(sql)
        
    
    def conn(self, readonly = False, tablename = ''):
        if self.dmc:
            mysql_conf = self.dmc_find_node(readonly, tablename)
            return self._conn(mysql_conf)

        if not readonly:
            mysql_conf = self.db_conf['mysql']['writerurl']
        else:
            mysql_conf = self.db_conf['mysql']['readerurl']
        return self._conn(mysql_conf)

    def _conn(self, mysql_conf_str):
        t = re.search('^(?P<user>([0-9a-zA-Z-_\.]*?))/[\'\"]?(?P<passwd>([\s\S]*?))[\'\"]?@(?P<host>([0-9a-zA-Z\._-]*?)):(?P<port>(\d*?))/(?P<db>([0-9a-zA-Z-_])*?)$',mysql_conf_str)
        d = t.groupdict()

        c = MySQLdb.connect(host   = d['host'],
                            port   = int(d['port']),
                            user   = d['user'],
                            passwd = d['passwd'],
                            db     = d['db'],
                            )
        c.set_character_set('utf8')
        c.autocommit=1
        return c

    def queryexecute(self,sql, tablename = ''):
        if sql.lower().find('select') == 0:
            db = self.conn(readonly = True, tablename = tablename)
            #print 'R:',sql
        else:
            db = self.conn(readonly = False, tablename = tablename )
            #print 'W:',sql
        c=db.cursor()
        rows_examined = 0
        try:
            try:
                c.execute(sql)
            except OperationalError , e:
                if e[0] == 1203:
                    print '1203 Error max_user_connections, retry...'
                    time.sleep(0.01)
                    c.execute(sql)
                else:
                    raise e
            except ProgrammingError , e:
                if sql.lower().find('select') == 0 and e[0] == 1146:
                    raise TableNotExists(e[1])
                else:
                    raise e
                
            if sql.lower().find('load ') == 0:
                d = db.info()
                if d:  #'Records: 10  Deleted: 0  Skipped: 0  Warnings: 0'
                    d = dict([i.split(':') for i in d.split('  ')])
                    d = dict([(i[0], int(i[1])) for i in d.items()])
                else:
                    d = {'Records':c.rowcount}
            else:
                d = c.fetchall()
                c.execute('SHOW STATUS LIKE "Handler_read%"')
                stat = c.fetchall()
                for i in stat:
                    if i[0] in ('Handler_read_next','Handler_read_rnd_next'):
                        rows_examined += int(i[1])
        finally:
            c.close()
            db.close()
        return {'Data':d, 'ProcessedRowsDisk':rows_examined, 'ProcessedRowsMem':0}

    def query_append(self, mycursor, tablename ,values):
        i_sql = 'insert into ' +tablename+ ' values ("' + '","'.join(values) + '")'
        try:
            mycursor.execute(i_sql)
            return 'insert'
        except:
            pass
        s_set = ','.join( [i[0] + '= '+i[0]+ '+' + values[i[1]]  for i in self.nonpk] )
        s_where = ' and '.join( [i[0] + '="' + values[i[1]] + '"'  for i in self.pk ] )
        u_sql = 'update '+tablename+' set ' +s_set +' where '+ s_where
        mycursor.execute(u_sql)
        return 'update'
        
    def query(self,s,iscache=True,refresh=False,tablename = ''):
        if not iscache:
            return self.queryexecute(s, tablename)
        from djutils.views import sqlcache
        m=md5.new()
        m.update(s)
        ky=m.hexdigest()
        ky = 'jd_'+ky

        if not refresh:
            v = sqlcache.get(ky)
            if v:
                print 'CACHE HIT:',v['ProcessedRowsMem'],s
                return v
            else:
                info = 'CACHE MISS:'
        else:
            info = 'CACHE REFRESH:'
        try:
            rst = self.queryexecute(s, tablename)
        except TableNotExists,e:
            print info,e
            return {'Data':(),'ProcessedRowsMem':0,'ProcessedRowsDisk':0}
        except TableNotExistsInDMC,e:
            print info,e
            return {'Data':(),'ProcessedRowsMem':0,'ProcessedRowsDisk':0}
        print info,rst['ProcessedRowsDisk'],s
        mem_rst = {}
        mem_rst['Data'] = rst['Data']
        mem_rst['ProcessedRowsMem'] = rst['ProcessedRowsDisk']
        mem_rst['ProcessedRowsDisk'] = 0
        sqlcache.set(ky,mem_rst,60*60*24)
        return rst


    def multithreadquery(self,sql,step_minute,pageby,refresh,tablename):
        rst=self.query(sql,refresh=refresh, tablename = tablename)
        t = rst['Data']
        rows_disk = rst['ProcessedRowsDisk']
        rows_mem = rst['ProcessedRowsMem']
        self.multithreadlock.acquire()
        self.multithreadresult = self.multithreadresult + t
        self.rowsfromdisk = self.rowsfromdisk + rows_disk
        self.rowsfrommem = self.rowsfrommem + rows_mem
        
        if str(step_minute) == '0':
            if pageby:
                pagebynum = len(pageby)
                x={}
                for i in self.multithreadresult:
                    k = tuple(i[:pagebynum])
                    if x.get(k):
                        #v = [ x[k][j+1] + i[j+1]  for j in range(len(x[k])-pagebynum)]
                        v = [ x[k][-1-j] + i[-1-j]  for j in range(len(x[k])-pagebynum)]
                        #v.insert(0,k)
                        v = list(k) + v
                        x[k] = v
                    else:
                        x[k] = i
                self.multithreadresult = tuple(x.values())
            else:
                x=[]
                for i in self.multithreadresult[0]:
                    x.append(0)
                for i in  self.multithreadresult:
                    x = [ x[j]+i[j] for j in range(len(i)) ]
                self.multithreadresult = (x,)
        self.multithreadlock.release()

    
    def gettablename(self,starttime=None):
        split_idx = self.db_conf['mysql']['table_split_idx']
        if starttime:
            if len(starttime) < split_idx:
                raise SpecifiedTimeTooShort('The time `'+starttime+'` is too short(<'+str(split_idx)+') to confirm the Table')
            return self.tableprefix+starttime[:split_idx]
        else:
            return self.tableprefix+time.strftime('%Y%m%d%H%i',time.localtime())[:split_idx]
    
    def createtable(self,tablename):
        crtsql="create table "+tablename+" ("
        for col in self.meta_db:
                crtsql=crtsql+col[0]+" "+col[1]+","
        crtsql=crtsql[:-1]+");"
        try:
            self.query(crtsql,iscache=False,tablename = tablename)
        except TableNotExistsInDMC:
            self.dmc_add_newtable(tablename)
            self.query(crtsql,iscache=False,tablename = tablename)


    def droptable(self, tablename):
        dropsql = 'drop table '+tablename
        self.query(dropsql,iscache=False,tablename = tablename)
        if self.dmc:
            self.dmc_remove_table(tablename)


    def loadfile2db_append(self,file,tablename,fields_terminated=" "):
        try:
            self.createtable(tablename)
            newtable = True
        except:
            newtable = False
        if newtable:
            return self.loadfile2db(file,tablename,fields_terminated)

        db = self.conn(readonly = False, tablename = tablename)
        cur = db.cursor()
        insert = 0
        update = 0
        err = 0
        rec = 0
        f = open(file,'rb')
        while True:
            try: l = f.next()
            except StopIteration: break
            rec += 1
            values = l[:-1].split(fields_terminated)
            try:
                r = self.query_append(cur, tablename, values)
                if r == 'insert':
                    insert += 1
                elif r == 'update':
                    update += 1
            except:
                print 'append error:',traceback.format_exc()
                err += 1
            
        f.close()
        cur.close()
        db.close()
        return {'Records': rec,  'Added':insert ,  'Updated':update,  'Errors': err} 
            
            
    def loadfile2db(self,file,tablename,fields_terminated=" ",load_mode = ''):
        from warnings import filterwarnings
        filterwarnings('ignore', category = Warning)
        try:
            self.createtable(tablename)
        except:
            #print 'table ',tablename,'exits'
            pass
        loadsql='load data local infile "'+file+'" '+load_mode+' into table '+tablename+'  fields terminated by "'+fields_terminated+'";'
        r = self.query(loadsql,iscache=False, tablename = tablename)
        return r

    def latest_timeline(self):
        sql0 = 'select max('+self.timefield+'), \
        date_format(date_add(concat(max('+self.timefield+'),"00"),interval -1 day),"%Y%m%d%H%i") \
        from '
        tablename = self.gettablename()
        sql = sql0 + tablename
        try:    
            return self.query(sql,iscache=False, tablename = tablename)
        except:
            yestd = time.strftime('%Y%m%d%H%M',time.localtime(time.time()-60*60*24))
            tablename = self.gettablename(yestd)
            sql = sql0 + tablename
            return self.query(sql,iscache=False, tablename = tablename)


    def distinct(self,field):
        table=self.gettablename(time.strftime('%Y%m%d',time.localtime(time.mktime(time.localtime())-60*60*24)))
        sql='select distinct '+field+' from '+table
        r=self.query(sql, table)['Data']
        return tuple([ i[0] for i in r ])


    def rawget(self,q_dict,step_minute=None): #query_dict  #step(time): 5 (unit:minute)
        if not step_minute:
            if not q_dict.has_key('_tstep'):
                step_minute=5
            else:
                step_minute=q_dict['_tstep']

        time1=time.time()
        time_field='date_format(date_add(concat('+self.timefield+',"00") ,interval -mod(right('+self.timefield+',2),'+str(step_minute)+') minute),"%Y/%m/%d %H:%i")'
        querylist=[]
        display_fields = []
        sql_s = 'select '  #select sql
        if str(step_minute) != '0':
            sql_s=sql_s+time_field+', '
            display_fields.append('时间')
        if q_dict.get('_pageby',''):
            #sql_s=sql_s+q_dict['_pageby']+','
            for j in q_dict['_pageby']:
                if j in self.fields_alias.keys():
                    display_fields.append(self.fields_alias[j][1])
                    j = self.fields_alias[j][0]
                else:
                    try:
                        fd_name = [o[2] for o in self.meta_db if o[0] == j][0]
                    except:
                        fd_name = j
                    display_fields.append(fd_name)
                sql_s = sql_s + j + ','
        for i in q_dict['_fields']:
            if i in self.fields_alias.keys():
                display_fields.append(self.fields_alias[i][1])
                i = self.fields_alias[i][0].replace('_minutes',str(step_minute))
            else:
                try:
                    fd_name = [o[2] for o in self.meta_db if o[0] == i][0]
                except:
                    fd_name = i
                display_fields.append(fd_name)
            sql_s=sql_s+i+','
        sql_s = sql_s[:-1]+' from '
        sql_w = ' where '   #where sql
        if not q_dict.has_key('_s'):
            stime=time.strftime('%Y%m%d0000')
            etime=time.strftime('%Y%m%d%H%M')
        else:
            stime=q_dict['_s']
            if not q_dict.has_key('_e'):
                etime=time.strftime('%Y%m%d%H%M')
            else:
                etime=q_dict['_e']
        try:
            querylist=self.generate_querylist(stime,etime)
        except ValueError:
            raise URLParameterError('Time Format Error  `start`:'+stime+' `end`:'+etime)

        for i in q_dict['_filters']:
            sql_w = sql_w+i+' and '

        if str(step_minute) != '0':
            if q_dict.get('_pageby',''):
                #sql_g = ' group by '+time_field+','+q_dict['_pageby']
                sql_g = ' group by '+time_field
                for j in q_dict['_pageby']:
                    if j in self.fields_alias.keys():
                        j = self.fields_alias[j][0]
                    sql_g = sql_g + ',' + j
            else:
                sql_g = ' group by '+time_field
        else:
            if q_dict.get('_pageby',''):
                #sql_g = ' group by '+q_dict['_pageby']
                sql_g = ' group by '
                for j in q_dict['_pageby']:
                    if j in self.fields_alias.keys():
                        j = self.fields_alias[j][0]
                    sql_g = sql_g + j + ','
                sql_g = sql_g[:-1]
            else:
                sql_g = ''

        mythread = []
        debugout = []
        for i in querylist:
            sql=sql_s+i[0]+sql_w+self.timefield+' >= '+i[1]+' and '+self.timefield+' <= '+i[2]+sql_g    
            args=(sql,step_minute,q_dict.get('_pageby',''),q_dict.has_key('_refresh'), i[0])
            t=Thread(target=self.multithreadquery,args=args)
            mythread.append(t)
            debugout.append( dict(zip(('sql','_tstep','_pageby','_refresh','tablename'), args) ))

        if q_dict.has_key('_debug'):
            raise DebugPrint(debugout)
            
        for i in mythread:
            i.start()
        for i in mythread:
            i.join()
        data= list(self.multithreadresult)
        data.sort()
        rows_disk = self.rowsfromdisk
        rows_mem = self.rowsfrommem
        self.multithreadresult=()
        self.rowsfromdisk = 0
        self.rowsfrommem = 0
        elapsed = round(time.time()-time1,3)
        print '[Data.rawget] Elapsed:',elapsed,'ProcessedRowsDisk:',rows_disk,'ProcessedRowsMem:',rows_mem,q_dict
        return {'Data':data, 'Metadata':display_fields, 'Elapsed':str(elapsed)+'s', 'ProcessedRowsDisk':str(rows_disk)+' rows', 'ProcessedRowsMem':str(rows_mem)+' rows', 'ResultCount':str(len(data))+' rows'}
   

    def get(self,q_dict,step_minute=None): #query_dict  #step(time): 5 (unit:minute)
        rst = self.rawget(q_dict,step_minute)
        data = rst['Data']
        if not data:
            return rst
        if not q_dict.get('_pageby',''):
            return rst
        elif len(q_dict['_pageby'])>1:
            return rst
        elif len(q_dict['_fields'])>1:
            return rst
        if str(q_dict.get('_tstep','')) == '0':
            return rst
        if q_dict.has_key('_rawdata'):
            return rst
        time1 = time.time()
        pagebys = {}.fromkeys([i[1] for i in data]).keys()
        l = len(data[0])
        thistime = data[0][0]
        thispageby = []
        adddata = []
        for i in data+[['0','x']]:
            if thistime == i[0]:
                thispageby.append(i[1])
            else:
                x = copy.copy(pagebys)
                for p in thispageby:
                    x.remove(p)
                for p in x:
                    adddata.append(tuple([thistime,p]+[0 for j in range(l-2)]))
                thispageby = [i[1],]
                thistime = i[0]
                
        newdata = data+adddata
        newdata.sort()
        cleaned = self.dataclean(newdata,q_dict.get('_dataclean',5))
        rst['Data'] = cleaned
        elapsed = round(time.time() - time1)
        elapsed += float(rst['Elapsed'][:-1])
        rst['Elapsed'] = str(elapsed)+'s'
        rst['ResultCount'] = str(len(cleaned))+' rows'
        print '[Data.get] Elapsed:',rst['Elapsed'],'ProcessedRowsDisk:',rst['ProcessedRowsDisk'],'ProcessedRowsMem:',rst['ProcessedRowsMem'],q_dict
        return rst

    def dataclean(self,data,threshold):  #need pageby
        threshold = int(threshold)
        max_v = 0
        max_e = {}
        noisedata = []
        newdata = []
        for i in data:
            if i[-1] > max_v : max_v = i[-1]
            if max_e.get(i[1],''):
                if i[-1] > max_e[i[1]]:
                    max_e[i[1]] = i[-1]
            else:
                max_e[i[1]] = i[-1]
        for i in max_e:
            v = max_e[i] or 0
            if 100*(float(v)/float(max_v))<threshold:
                noisedata.append(i)
        for i in data:
            if i[1] not in noisedata:
                newdata.append(i)
        return newdata
        

    def generate_querylist(self,start,end): #return tablename,starttime,endtime
        querylist=[]
        split_idx = self.db_conf['mysql']['table_split_idx']
        if start[:split_idx] == end[:split_idx]:
            return [(self.gettablename(start),"'"+start+"'","'"+end+"'")]
        if split_idx == 4:
            seq = rrule.YEARLY
            postfix_s = '01010000'
            postfix_e = '12312359'
            fmt = '%Y'
        elif split_idx == 6:
            seq = rrule.MONTHLY
            postfix_s = '010000'
            postfix_e = '312359'
            fmt = '%Y%m'
        elif split_idx == 8:
            seq = rrule.DAILY
            postfix_s = '0000'
            postfix_e = '2359'
            fmt = '%Y%m%d'
        elif split_idx == 10:
            seq = rrule.HOURLY
            postfix_s = '00'
            postfix_e = '59'
            fmt = '%Y%m%d%H'
 
        _start = start[:split_idx]
        _end = end[:split_idx]
        for i in list(rrule.rrule(seq, dtstart=parse(_start+postfix_s),until=parse(_end+postfix_s))):
            v = i.strftime(fmt)
            if _start == v:
                querylist.append((self.gettablename(v), "'"+start+"'", "'"+v+postfix_e+"'"))
            elif _end == v:
                querylist.append((self.gettablename(v), "'"+v+postfix_s+"'", "'"+end+"'"))
            else:
                querylist.append((self.gettablename(v), "'"+v+postfix_s+"'", "'"+v+postfix_e+"'"))
        #print 'ql:',querylist
        return querylist
            

