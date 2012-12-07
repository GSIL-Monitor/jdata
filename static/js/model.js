/**
 * @author timger <yishenggudou@gmail.com>
 * @timger http://weibo.com/zhanghaibo
 * twitter @yishenggudou http://twitter.com/yishenggudou
 * @yishenggudou http://twitter.com/yishenggudou
 * Copyright (c) 2008-2011 timger - released under MIT License 
 */


/* see https://github.com/powmedia/backbone-deep-model
 *
 *
 */

Class.Model.ALLOWIPS = Backbone.Model.extend({ 
    defaults:{ ip:""}
    })

Class.Model.DataBase = Backbone.Model.extend({
    defaults:{
                db_host:"",
                db_port:"",
                db:"",
                db_user:"",
                db_passwd:""
             }
    })
Class.Model.DB = Backbone.Model.extend({
    defaults:{
                 mysql:{
                           writer:new Class.Model.DataBase({}),
                           reader:new Class.Model.DataBase({})
                       },
                writerurl:'',
                readerurl:'',
                table_split_idx:"10",
                tableprefix:"test_"
             },
     initialize:function(){
        if (!this.get('writerurl')){
            var obj = this.get('mysql').writer.toJSON()
            if (obj.db_user && obj.db_passwd && obj.db && obj.db_host && obj.db_port){
                var writerurl = obj.db_user+'/'+obj.db_passwd+'@'+obj.db_host+':' +obj.db_port+'/'+obj.db;
                this.set({writerurl:writerurl})
            }
        }
        if (!this.get('readerurl')){
            var obj = this.get('mysql').reader.toJSON()
            if (obj.db_user && obj.db_passwd && obj.db && obj.db_host && obj.db_port){
                var readerurl = obj.db_user+'/'+obj.db_passwd+'@'+obj.db_host+':' +obj.db_port+'/'+obj.db;
                this.set({readerurl:readerurl})
            }
        }
                }

    })

Class.Model.fields_alias = Backbone.Model.extend({
    defaults:{
                 name:"",
                 lambda:"",
                 alias:""
             },
    validate: function(attrs) {
        if (!attrs.name.match(/[a-zA-Z0-9\-\.\_]+?$/g)){
                console.log("名字必须为[a-zA-Z0-9i\-\.\_]")
            }
        else if (!attrs.alias.match(/[a-zA-Z0-9\-\.\_]+?$/g)){
                console.log("名字必须为[a-zA-Z0-9-._]")
            }
    }
    })
Class.Collection.METADB = Backbone.Collection.extend({
    model:Class.Model.fields_alias
    })

Class.Collection.FIELDS_ALIAS = Backbone.Collection.extend({
    model:Class.Model.fields_alias
    })
Class.Collection.ALLOWIPS = Backbone.Collection.extend({
    model:Class.Model.ALLOWIPS
    })
Class.Model.Config = Backbone.Model.extend({
        defaults:{
                 DB:new Class.Model.DB({}),
                 METADB: new Class.Collection.METADB([]),
                 NAME:"",
                 KEY:"",
                 FIELDS_ALIAS:new Class.Collection.FIELDS_ALIAS([]),
                 SHOW_IN_QUERY:true,
                 ALLOWIPS:new Class.Collection.ALLOWIPS([]),
                 SHOW_QUERY_LABLE:"是否在各种查中显示",
                 PRIMART_KEY:[{name:''}],
             }
        })

Class.Model.Conf = new Class.Model.Config({})

Class.Model.Conf.tojson = function(){
                    var rst = {};
                    var DB = {};
                    DB.mysql = {}
                    DB.mysql.reader = Class.Model.Conf.get('DB').get('mysql').reader.toJSON()
                    DB.mysql.writer = Class.Model.Conf.get('DB').get('mysql').writer.toJSON()
                    DB.table_split_idx = Class.Model.Conf.get('DB').get('table_split_idx');
                    DB.tableprefix = Class.Model.Conf.get('DB').get('tableprefix');
                    DB.writerurl = Class.Model.Conf.get('DB').get('writerurl');
                    DB.readerurl = Class.Model.Conf.get('DB').get('readerurl');
                    DB.mysql.writerurl = DB.writerurl;
                    DB.mysql.readerurl = DB.readerurl;
                    DB.mysql.table_split_idx = DB.table_split_idx;
                    DB.mysql.tableprefix = DB.tableprefix;
                    rst.DB =  DB;
                    rst.METADB =  Class.Model.Conf.get('METADB').toJSON();
                    rst.FIELDS_ALIAS =  Class.Model.Conf.get('FIELDS_ALIAS').toJSON();
                    rst.PRIMART_KEY =  Class.Model.Conf.get('PRIMART_KEY');
                    rst.NAME = Class.Model.Conf.get('NAME');
                    rst.KEY = Class.Model.Conf.get('KEY');
                    rst.ALLOWIPS = Class.Model.Conf.get('ALLOWIPS').toJSON();
                    rst.SHOW_IN_QUERY = Class.Model.Conf.get('SHOW_IN_QUERY');
                    return rst
                    }
