#!/bin/bash




#############  CONFIG #############

PYTHON27=/usr/local/python2.7/bin/python
PIDFILE=/var/run/jdata.pid
OUTLOG=/var/log/jdata.out.log
ERRLOG=/var/log/jdata.err.log
PORT=18017
MEMCACHED=10.11.50.44:11211

###################################



cd `dirname $0`
basedir=`pwd`

function help(){
 echo
 echo "Usage:"
 echo -e "\t $0 start|stop|restart"
 echo
 exit
 }

function start(){
   $PYTHON27 manage.py runfcgi method=threaded host=127.0.0.1 port=$PORT pidfile=$PIDFILE outlog=$OUTLOG errlog=$ERRLOG
}

function stop(){
   [ -f $PIDFILE ]  && (kill -9 `cat $PIDFILE`;rm -f $PIDFILE) || echo "Jdata is running?"
}


if [ -z $1 ];then
  help
fi

sed  's/CACHE_BACKEND.*/CACHE_BACKEND = "memcached:\/\/'$MEMCACHED'\/?timeout=3600"/g' settings.py -i

case $1 in 
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  *)
    help
    ;;
esac




