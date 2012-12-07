#_*_coding:utf-8 _*_
# Create your views here.

from jdata.core.datamodel import DataModel
from jdata.djutils.views import return_http_json
from jdata.djutils.exceptions import AccessDenied



def q(request):
    """
    等同于qjson方法，返回字典JSON数据 ，除了包含结果数据，还包含处理时长、处理的记录条数、返回的字段含义等等
     {'Data':data, 'Metadata':display_fields, 'Elapsed':elapsed, 'RowsFromDisk':rows_disk, 'RowsFromMem':rows_mem}
    e.g. http://jdata.qiyi.domain/data/q?_o=cdnbw&_tstep=5&cdn_type=qihu360&_dataclean=0&_fields=request&s=201202211504&e=201203041504&_lines=fields
    wiki: http://wiki.qiyi.domain/display/sys/Jdata
    """
    path=request.get_full_path()
    DM=DataModel(path=path)
    client = request.META.get('REMOTE_ADDR','')
    if DM.ALLOWIPS and (client not in DM.ALLOWIPS):
        raise AccessDenied('Your IP `'+client+'` is not trusted  for `'+DM.objectname+'`.')
    rst=DM.Data.get(DM.get_query_dict(path))
    return return_http_json(rst)
        
