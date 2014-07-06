from bottle import route, run
from json import dumps
from requestmanager import *


@route('/hello')
def hello():
    return "Hello World!"

#switch_list = ["10.0.0.1:9999","10.0.0.2:9998","10.0.0.3:9997"]

@route("/stats/<start_ip>/<end_ip>/<earliest_idx>/<num_entries>",method='GET')
def get_path_stats(start_ip, end_ip,earliest_idx,num_entries):
   link_capacity = find_link_cap(start_ip,end_ip)
   path = find_path(start_ip, end_ip)
   print path
   start_monitor()
   jpip_stats = requestmanager(path,link_capacity,int(earliest_idx),int(num_entries))
   return dumps(jpip_stats)

def find_link_cap(start_ip,end_ip):
   if start_ip == "1":
      retVal = [640000,1280000]
      return retVal
   if end_ip == "1":
      retVal = [640000,1280000]
      return retVal   
def find_path(start_ip,end_ip):
   if start_ip == "1":
      retVal = ["s1-eth2","eth1"]
      return retVal
   if end_ip == "1":
      retVal = ["s2-eth2","eth0"]
      return retVal
# STATICALY DEFINE LINKS IN HERE.


run(server='paste',host='10.0.0.254', port=8080, debug=True)
