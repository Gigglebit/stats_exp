from bottle import route, run
from json import dumps
from requestmanager import *
from myGlobal import myGlobal
from threading import Thread
from urlparse import urlparse
import httplib, sys
import numpy as np
import json
from Queue import Queue
concurrent = 200
q = Queue(concurrent * 2)
jpip_stats = []
lock = threading.Lock()
def doWork():
    while True:
        url = q.get()
        res, url = getStatus(url)
        doSomethingWithResult(res, url)
        q.task_done()


def getStatus(ourl):
    try:
        url = urlparse(ourl)
        conn = httplib.HTTPConnection(url.netloc)   
        conn.request("GET", url.path)
        res = conn.getresponse()
        return res, ourl
    except:
        return "error", ourl

def doSomethingWithResult(res, url):
    print res.status, url
    lock.acquire()
    result = res.read()
    json_data = json.loads(result)
    if json_data["response"] != "started monitoring":
      jpip_stats.append(json_data["response"])
    lock.release()



@route('/hello')
def hello():
    return "Hello World!"

#switch_list = ["10.0.0.1:9999","10.0.0.2:9998","10.0.0.3:9997"]
@route("/stats/<start_ip>/<end_ip>/<earliest_idx>/<num_entries>",method='GET')
def get_path_stats(start_ip, end_ip,earliest_idx,num_entries):
   '''
   This function is the main Northbound API 
   '''
   link_capacity = find_link_cap(start_ip,end_ip)
   path = find_path(start_ip, end_ip)
   hosts = [
      "10.1.1.4",
      "10.1.1.5"
   ]
   intfs = [
      "swp3",
      "swp1"
   ]
   port = "8080"
   global jpip_stats 
   jpip_stats = []
   start_urls = []
   stats_urls = []
   num_hosts = 0
   for host in hosts:
      endpoint = "http://"+host+":"+port
      start_urls.append(endpoint+"/start")
      stats_urls.append(endpoint+"/stats/"+intfs[num_hosts]+"/0/0")
      num_hosts+=1
   for i in range(concurrent):
       t = Thread(target=doWork)
       t.daemon = True
       t.start()
   try:
       for url in start_urls:
           q.put(url.strip())
       q.join()
       for url in stats_urls:
           q.put(url.strip())
       q.join()
   except KeyboardInterrupt:
       sys.exit(1)


   #print path

   #print "a1"

   #print "a2"
   #fname="./test/newfile%d.txt"%int(myGlobal.idx-1)
   #if not os.path.isfile(fname):
	#print "haha"
   #file = open(fname, "a")
   #file.write("%s"%jpip_stats)
   #file.close()

   lock.acquire()
   results = jpip_stats
   lock.release()
   # find_the_threshold(result)
   result = combine_results(num_hosts,results)
   #print "a3"
   return json.dumps({"response":result})

# def find_the_threshold(lists):
#    for i in range(len(lists)):
#       print lists[i]
def combine_results(num_hosts, results):
   result = []
   npr = np.array(results)
   print npr.shape
   if npr.shape == (2, 1):
      return ""

   tmp = None
   final = None
   for i in range(num_hosts):
      if i == 0:
         tmp = set(npr[i,:,0])
      else:
         final = tmp.intersection(set(npr[i,:,0]))
   agent_index = sorted(final)
   idx = 0
   delta_t = 0.0
   most_backlogged_bytes = 0.0
   most_bandwidth_used_bytes = 0.0
   total_delay = 0.0
   for i in range(len(agent_index)):
      l = []
      l.append(agent_index[i])
      for j in range(num_hosts):
         diff = agent_index[i] - npr[j,i,0]
         if npr[j,i+diff,1] > delta_t:
            delta_t = rnd(npr[j,i+diff,1],4)
         if npr[j,i+diff,2] > most_backlogged_bytes:
            most_backlogged_bytes = npr[j,i+diff,2]
         if npr[j,i+diff,3] > most_bandwidth_used_bytes:
            most_bandwidth_used_bytes = npr[j,i+diff,3]
         total_delay+=npr[j,i+diff,4]
      l.append(delta_t)
      l.append(most_backlogged_bytes)
      l.append(most_bandwidth_used_bytes)
      l.append(total_delay)
      result.append(l)
   return result

def find_link_cap(start_ip,end_ip):
   if start_ip == "10.0.0.1":
      retVal = [5,10]#[5Mbps,10Mbps]
      return retVal
   if end_ip == "10.0.0.2":
      retVal = [5,10]
      return retVal   
def find_path(start_ip,end_ip):
   if start_ip == "10.0.0.1":
      retVal = ["s1-eth2","s2-eth1","s3-eth2"] # the first two are the relevant switches, the last one is were to get the delay
      return retVal
   if end_ip == "10.0.0.2":
      retVal = ["s2-eth2","s1-eth1","s4-eth2"] # the first two are the relevant switches, the last one is were to get the delay
      return retVal
# STATICALLY DEFINE LINKS IN HERE.

run(server='cherrypy',host='10.1.1.1', port=8080, debug=True)
