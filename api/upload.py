#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdata.djutils.views import return_http_json
from jdata.djutils.exceptions import UploadDataMethodError,UploadDataParameterError,ObjectPKNotFound
from jdata.core.datamodel import DataModel
from os import mkdir,remove
from os.path import isdir,join
import time
    

def upload_result_file(request):
    """
    上传文件，做入库处理  POST 方法
    参数：
    file=@filename   本地文件
    _o=cdnbw         数据object名字
    _s=201203201340   这份数据的时间戳，请注意该文件中的数据时间跨度不得超过定义的拆表时间区间（table_split）
    _t=,             数据的分隔符，默认空格
    data_exists_action  数据如果存在（主键冲突）的处理方法，支持3种模式：    ignore (Default) | replace | append
                        ignore:    如果发现数据已经存在，则忽略；不存在的数据可以成功导入
                        replace:   如果已存在，则替换掉旧数据
                        append:    如果已存在，则往上累加（除主键外的其他字段，当存在百分比类似的数据时不适合使用append，除非确认可以对这些字段做累加）

    e.g. curl  -F file=@filename -F _o=cdnbw -F _s=201203201340 -F '_t=,' -F data_exists_action=replace http://jdata.qiyi.domain/api/uploadresultfile

    """
    uploaddir = '/tmp/jdata/'
    if not isdir(uploaddir):mkdir(uploaddir)
    if request.method == 'POST':
        file = request.FILES['file']
        filename = file.name
        try:obj = request.POST['_o']
        except:raise UploadDataParameterError("parameter `_o` is required")
        DM = DataModel(obj)
        try:timeline = request.POST['_s']
        except:raise UploadDataParameterError("parameter `_s` is required")
        fields_terminated = request.POST.get('_t',' ')

        objdir = join(uploaddir,obj)
        if not isdir(objdir):
            mkdir(objdir)
        now = time.strftime('%Y%m%d%H%M%S',time.localtime())
        tmpfile = join(objdir,now+'_'+timeline+'_'+filename)
        f = open(tmpfile,'wb')
        f.write(file.read())
        f.close()
        data_exists_action = request.POST.get('data_exists_action','ignore')
        t1 = time.time()

        if data_exists_action in('ignore','replace', 'append'):
            tablename = DM.Data.gettablename(timeline)
            if data_exists_action == 'ignore':
                load_mode = ''
            elif data_exists_action == 'replace':
                if not DM.Data.pk:
                    raise ObjectPKNotFound('No PK Found For this Data `'+obj+'` ,so you can not use parameter `replace`')
                load_mode = 'replace'
            elif data_exists_action == 'append':
                if not DM.Data.pk:
                    raise ObjectPKNotFound('No PK Found For this Data`'+obj+'` ,so you can not use parameter `append`')
                rst = DM.Data.loadfile2db_append(tmpfile,tablename,fields_terminated)
                print 'uploadresult:',str(int(time.time()-t1))+'s',tmpfile,rst
                return return_http_json(rst)
            rst = DM.Data.loadfile2db(tmpfile,tablename,fields_terminated,load_mode)
            print 'uploadresult:',str(int(time.time()-t1))+'s',tmpfile,rst
            try: remove(tmpfile)
            except: pass
            return return_http_json(rst)
        else:
            raise UploadDataParameterError(" Unknown value `"+data_exists_action+"` for data_exists_action")
    else:
        raise UploadDataMethodError("""Please POST your data like this: curl  -F file=@filename -F _o=cdnbw -F _s=201203201340 -F '_t= '  http://jdata.qiyi.domain/api/uploadresultfile""")
        
