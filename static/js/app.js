/**
 * @author timger <yishenggudou@gmail.com>
 * @timger http://weibo.com/zhanghaibo
 * twitter @yishenggudou http://twitter.com/yishenggudou
 * @yishenggudou http://twitter.com/yishenggudou
 * Copyright (c) 2008-2011 timger - released under MIT License 
 */


renderto =  function(container,elem){
    var func = function(){
        return elem;
    } 

    return Class.View.render(container, func)

}

$(document).ready(function(){
    // 渲染需要的元素
    for (i in Class.View.renderlist){
        renderto(Class.View.renderlist[i][0],Class.View.renderlist[i][1]) 
    };
    //定时刷新写入的数据；
    window.P_total = setInterval(function(){
        var to_render = Class.Model.Conf.tojson();
        var template = $('#tmpl_total').html();
        var html = Mustache.to_html(template,to_render);
        $('#total_board').html(html) 
        },100)
    var steps =    [
                    [$('#step-one'),0],
                    [$('#step-two'),1],
                //    [$('#step-three'),2],
                    [$('#step-four'),3],
                    [$('#step-five'),4],
                    [$('#step-six'),5],
                    [$('#step-seven'),6],
                    [$('#step-finish'),7],
                    ]
    var nowshow = 0;
    _.each(steps,function(item){
            var el= $(item[0]);
            $(el).hide();
            })
    $(steps[nowshow][0]).show();
    $('#step-next').live('click',function(e){
            var i = nowshow+1;
            if (i > steps.length-1 ){
                i = 0;    
                }
            $(steps[nowshow][0]).slideUp().hide();
            $(steps[i][0]).slideUp(10).show();
            nowshow = i
            })
    $('#step-prev').live('click',function(e){
            var i = nowshow-1;
            if (i < 0){
                i = steps.length-1;    
                }
            $(steps[nowshow][0]).slideDown().hide();
            $(steps[i][0]).slideDown(10).show();
            nowshow = i
            })
       $(document).keydown(function(e){
        if (e.keyCode == 37 ){
            //left
            $('#step-prev').click();
        };
        if (e.keyCode == 38 ){
            //left
            $('#arrow_up').click();
        };
        if (e.keyCode == 39 ){
            //left
            $('#step-next').click();
        };
        if (e.keyCode == 40 ){
            //left
            $('#arrow_down').click();
        }
    });




    $('#finish').live('click',function(e){
            var data=Class.Model.Conf.tojson();
            var url = '/web/object/'+'';
            console.log(["post  data",data])
            window.data = data;
            if (!data.KEY.match(/[a-zA-Z0-9\_\-\.]+?/g)){
                alert("数据类型名字必须为[a-zA-Z\.+-]");
                return false;
                }
            $.get('/web/check',{key:data.KEY},function(msg){
                if (
                    (msg.success && location.pathname.match(/create/))
                    ||
                    ((!msg.success) && location.pathname.match(/web\/object/) )
                    ){
                    //创建的时候key不能重复
                    //修改的时候key可以重复 
                    $.post(url,{'data':JSON.stringify(data),key:data.KEY},function(data){
                            console.log(["保存数据到数据库",data])
                            if (data.success){
                                    alert("成功!");
                                }else{
                                    alert("失败!"+data.msg);
                                    } 
                            },'json') 
                }else{
                    alert("名字存在请重新选择名字");
                    return false;
                    }

            },'json')
            })    
    //加载数据源
    $.get(location.pathname,{type:"json"},function(data){
        console.log(["服务器获取数据",data]);
        Class.Model.Conf.set({KEY:data.KEY || location.pathname.split('/').pop()});
        Class.Model.Conf.set({NAME:data.NAME});
        Class.Model.Conf.set({SHOW_IN_QUERY:data.SHOW_IN_QUERY});
        Class.Model.Conf.get('ALLOWIPS').add((data.ALLOWIPS || []));
        Class.Model.Conf.get('FIELDS_ALIAS').add((data.FIELDS_ALIAS || []));
        Class.Model.Conf.get('METADB').add((data.METADB || []));
        Class.Model.Conf.get('DB').get('mysql').reader.set(data.DB.mysql.reader);
        Class.Model.Conf.get('DB').get('mysql').writer.set(data.DB.mysql.writer);
        Class.Model.Conf.get('DB').set({table_split_idx:data.DB.table_split_idx});
        Class.Model.Conf.get('DB').set({tableprefix:data.DB.tableprefix});
        Class.Model.Conf.get('DB').set({writerurl:data.DB.writerurl});
        Class.Model.Conf.get('DB').set({readerurl:data.DB.readerurl});
        if ((!data.DB.writerurl) && (!data.DB.readerurl)){
             Class.Model.Conf.get('DB').initialize()
        }
        if (location.pathname.match(/web\/object/)){
            console.log(["修改object"])
            $('#ui-key input').prop('disabled', true)
        }else{
            console.log(["创建object "])
            Class.Model.Conf.get('METADB').add({name:"ptime",lambda:"char(12)",alias:"ptime"}) 
            Class.Model.Conf.get('FIELDS_ALIAS').add({name:"timeline",lambda:"ptime",alias:"TimeLine"}) 
        }
    },'json').error(function(){
            console.log(["创建object "])
            Class.Model.Conf.get('METADB').add({name:"ptime",lambda:"char(12)",alias:"ptime"}) 
            Class.Model.Conf.get('FIELDS_ALIAS').add({name:"timeline",lambda:"ptime",alias:"TimeLine"}) 
        })
        
    })
