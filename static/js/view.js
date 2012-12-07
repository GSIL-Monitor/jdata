/**
 * @author timger <yishenggudou@gmail.com>
 * @timger http://weibo.com/zhanghaibo
 * twitter @yishenggudou http://twitter.com/yishenggudou
 * @yishenggudou http://twitter.com/yishenggudou
 * Copyright (c) 2008-2011 timger - released under MIT License 
 */

//see http://perka.github.com/backbone-ui/

Class.View.DB = {
                mysql:{
                    reader:{
                        db:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').reader,
                                 content:'db'
                                }).render(),
                        db_host:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').reader,
                                 content:'db_host'
                                }).render(),
                        db_port:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').reader,
                                 content:'db_port'
                                }).render(),
                        db_user:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').reader,
                                 content:'db_user'
                                }).render(),
                        db_passwd:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').reader,
                                 content:'db_passwd'
                                }).render(),
                           },
                    writer:{
                        db:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').writer,
                                 content:'db'
                                }).render(),
                        db_host:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').writer,
                                 content:'db_host'
                                }).render(),
                        db_port:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').writer,
                                 content:'db_port'
                                }).render(),
                        db_user:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').writer,
                                 content:'db_user'
                                }).render(),
                        db_passwd:new Backbone.UI.TextField({
                                 model:Class.Model.Conf.get('DB').get('mysql').writer,
                                 content:'db_passwd'
                                }).render(),
                           },
                    table_split_idx:new Backbone.UI.TextField({
                                        model:Class.Model.Conf.get('DB'),
                                        content:"table_split_idx"
                                        }).render(),
                    tableprefix:new Backbone.UI.TextField({
                                        model:Class.Model.Conf.get('DB'),
                                        content:"tableprefix"
                                        }).render(),
                      }
    }



//allow ips 
window.allowips = Class.Model.Conf.get('ALLOWIPS');
Class.View.IPS_LI = Backbone.View.extend({
    //三排输入列表
    initialize:function(){
               console.log(["allow ips"]);
               },
    render: function() {
            if (this.has_rendered){
                return
                }
            console.log(["start render..."]);
            $(this.el).empty();
            var that =  this;
            this.el.appendChild(new Backbone.UI.TextField({
                     model: this.model,
                     labelContent: 'ips',
                     content: 'ip',
                     onKeyPress:function(e){console.log(["key press",$(e.target).attr('id'),e,$(e.target)])},
                     onKeyUp:function(){console.log("key Up")}
                   }).render().el);
            this.el.appendChild(new Backbone.UI.Link({
                      content: '删除',
                      onClick: function(e){
                                    var t = $(e.target).parent().parent().parent().parent().parent().parent().parent().parent().attr('id');
                                    console.log(["删除绑定",this,that,$(e.target),that.model])
                                    allowips.remove(that.model)
                                    }
                    }).render().el);
            this.has_rendered = true;
            console.log(["render finish",this.has_rendered])
            }
        });
Class.View.IPS = new Backbone.UI.List({
            itemView: Class.View.IPS_LI,
            model: Class.Model.Conf.get('ALLOWIPS')
            }).render()
var addip = new Backbone.Model;
Class.View.ALLOWIPS = new Backbone.UI.TextField({
            model: addip,
            content: 'name',
            placeholder: '添加一个授权ip',
            onKeyPress: function(e) {
            console.log(["key press",$(e.target).attr('id'),e,$(e.target)])
            if (e.keyCode == 13) {
                    console.log(["添加字段model",addip.clone()])
                    var task = new Class.Model.ALLOWIPS({ip:addip.clone().get('name')})
                    Class.View.IPS.options.model.add(task);
                    addip.set({
                            name: undefined
                        });
                    }
            }
        }).render();


//---end allow ips



window.tasks = Class.Model.Conf.get('METADB');
Class.View.ThreeLi = Backbone.View.extend({
    //三排输入列表
    initialize:function(){
               console.log(["test..."]);
               },
    render: function() {
            if (this.has_rendered){
                return
                }
            console.log(["start render..."]);
            $(this.el).empty();
             //添加输入选项
           //输入姓名
           var that =  this;
           this.el.appendChild(new Backbone.UI.TextField({
                     model: this.model,
                     labelContent: 'name',
                     content: 'name',
                     onKeyPress:function(e){console.log(["key press",$(e.target).attr('id'),e,$(e.target)])},
                     onKeyUp:function(){console.log("key Up")}
                   }).render().el);
           //输入类型或者表达式
           this.el.appendChild(new Backbone.UI.TextField({
                     model: this.model,
                     labelContent: 'lambda',
                     content: 'lambda',
                     onKeyPress:function(){console.log("key press")},
                     placeholder: 'char(12),int,float'
                   }).render().el);
           //输入别名
           this.el.appendChild(new Backbone.UI.TextField({
                     model: this.model,
                     labelContent: 'alias',
                     onKeyPress:function(){console.log("key press")},
                     content: 'alias'
                   }).render().el); 
            //删除当前选项
            this.el.appendChild(new Backbone.UI.Link({
                      content: '删除',
                      onClick: function(e){
                                    var t = $(e.target).parent().parent().parent().parent().parent().parent().parent().parent().attr('id');
                                    console.log(["删除绑定",this,that,$(e.target),that.model])
                                    if (t == "FIELDS_ALIAS"){
                                        var tasks = Class.Model.Conf.get('FIELDS_ALIAS'); 
                                        tasks.remove(that.model)
                                    }else if (t == "METADB"){
                                        var tasks = Class.Model.Conf.get('METADB');
                                        tasks.remove(that.model)
                                    }
                                    }
                    }).render().el);
            this.has_rendered = true;
            console.log(["render finish",this.has_rendered])
            }
        })

Class.View.METADB = new Backbone.UI.List({
            itemView: Class.View.ThreeLi,
            model: Class.Model.Conf.get('METADB')
}).render()

var newItem = new Backbone.Model;
Class.View.METADB_INPUT = new Backbone.UI.TextField({
            model: newItem,
            content: 'name',
            placeholder: '添加一个新的字段',
            onKeyPress: function(e) {
            console.log(["key press",$(e.target).attr('id'),e,$(e.target)])
            if (e.keyCode == 13) {
                    console.log(["添加字段model",newItem.clone()])
                    var task = new Class.Model.fields_alias({name:newItem.clone().get('name')})
                    //tasks.add(newItem.clone());
                    Class.View.METADB.options.model.add(task);
                    newItem.set({
                            name: undefined
                        });
                    }
            }
        }).render();

Class.View.FIELDS_ALIAS = new Backbone.UI.List({
            itemView: Class.View.ThreeLi,
            model: Class.Model.Conf.get('FIELDS_ALIAS')
}).render()

var newItem_ = new Backbone.Model;
Class.View.FIELDS_ALIAS_INPUT = new Backbone.UI.TextField({
            model: newItem_,
            content: 'name',
            placeholder: '添加一个新的字段',
            onKeyPress: function(e) {
            if (e.keyCode == 13) {
                    console.log(["添加字段model",newItem_.clone()])
                    var task = new Class.Model.fields_alias({name:newItem_.clone().get('name')})
                    //tasks.add(newItem.clone());
                    Class.View.FIELDS_ALIAS.options.model.add(task);
                    newItem_.set({
                            name: undefined
                        });
                    }
            }
        }).render();


Class.View.SHOW_IN_QUERY = new Backbone.UI.Checkbox({
                                model: Class.Model.Conf,
                                content: 'SHOW_IN_QUERY',
                                labelContent: 'SHOW_QUERY_LABLE',
                            }).render();

Class.View.NAME = new Backbone.UI.TextField({
                        model: Class.Model.Conf,
                        content: 'NAME',
                        attributes :{style:"width:600px"},
                        placeholder:"如:实时带宽计算 -- 来自于cache log"
                    }).render();

Class.View.KEY = new Backbone.UI.TextField({
                        model: Class.Model.Conf,
                        content: 'KEY',
                        id:"ui-key",
                        placeholder:'like:cdnbw'
                    }).render();

Class.View.WRITERURL = new Backbone.UI.TextField({
                        model: Class.Model.Conf.get('DB'),
                        content: 'writerurl',
                        attributes :{style:"width:600px"},
                        id:"ui-writerurl",
                        placeholder:'cdn_master/cdn_master@bjct.syscdn.w.qiyi.db:5001/cdn'
                    }).render();

Class.View.READERURL = new Backbone.UI.TextField({
                        model: Class.Model.Conf.get('DB'),
                        content: 'readerurl',
                        attributes :{style:"width:600px"},
                        placeholder:'cdn_master/cdn_master@bjct.syscdn.r.qiyi.db:5001/cdn'
                    }).render();

Class.View.PRIMART_KEY = ''


 
Class.View.render = function (container, func) {
  // remove function wrapper and return statement 
  // from the code, then format it
  function beautify(func) {
  var code = func.toString();
  code = code.substring(code.indexOf('\n'));
  code = code.substring(0, code.lastIndexOf('return'));
  code = code.replace(/var lorem = \"[^\"]*"/, 'var lorem = "Lorem ipsum dolor sit..."');
  code = js_beautify(code, {
    indent_size : 2 
  });
  return code;
    }
  var code = beautify(func);

  var example = $.el.div(
    $.el.div({className : 'code'}, 
      $.el.pre({className : 'prettyprint'}, code)),
    $.el.div({className : 'result'}, 
      func().el),
    $.el.br({style : 'clear:both'}));
    
    var ref = $('.options', $(container)[0])[0];
    if(ref) {
      $(container)[0].insertBefore(example, ref);
    }
    else {
      $(container)[0].appendChild(example);
    }
}

Class.View.renderlist = [
    ["#DB-mysql-writer-db_host",Class.View.DB.mysql.writer.db_host],
    ["#DB-mysql-writer-db",Class.View.DB.mysql.writer.db],
    ["#DB-mysql-writer-db_port",Class.View.DB.mysql.writer.db_port],
    ["#DB-mysql-writer-db_user",Class.View.DB.mysql.writer.db_user],
    ["#DB-mysql-writer-db_passwd",Class.View.DB.mysql.writer.db_passwd],
    ["#DB-mysql-reader-db_host",Class.View.DB.mysql.reader.db_host],
    ["#DB-mysql-reader-db",Class.View.DB.mysql.reader.db],
    ["#DB-mysql-reader-db_port",Class.View.DB.mysql.reader.db_port],
    ["#DB-mysql-reader-db_user",Class.View.DB.mysql.reader.db_user],
    ["#DB-mysql-reader-db_passwd",Class.View.DB.mysql.reader.db_passwd],
    ["#DB-mysql-table_split_idx",Class.View.DB.mysql.table_split_idx],
    ["#DB-mysql-tableprefix",Class.View.DB.mysql.tableprefix],
    ['#NAME',Class.View.NAME],
    ['#KEY',Class.View.KEY],
    ["#SHOW_IN_QUERY",Class.View.SHOW_IN_QUERY],
    ["#METADB",Class.View.METADB],
    ["#METADB_INPUT",Class.View.METADB_INPUT],
    ['#FIELDS_ALIAS',Class.View.FIELDS_ALIAS],
    ['#FIELDS_ALIAS_INPUT',Class.View.FIELDS_ALIAS_INPUT],
    ['#IPS',Class.View.IPS],
    ['#ALLOWIPS',Class.View.ALLOWIPS],
    ['#READERURL',Class.View.READERURL],
    ['#WRITERURL',Class.View.WRITERURL],
    ]

