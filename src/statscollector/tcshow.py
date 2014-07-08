#!/bin/python
import os,re
import time
import subprocess
import threading
import Queue
from myGlobal import myGlobal
#from threading import *
############################
# This is a simple function for extracting useful info from tc -s qdisc show
# entries[]:
# Extracted columns include:
# 0 1 2 3 4 5 6 7 8 9
# idx RootNo. DevName Sent(Bytes) Sent(Packets) Dropped(Packets) Overlimits(Bytes) Requeues Backlog(Bytes) Backlog(Packets)


# RootNo is related to multiple Queues of an interface pls ignore at the current stage
#
############################
MAX_BUF = 100
#idx = 0
shared_Q = Queue.Queue(2)
tc_dict ={}
entry_keys = ['RootNo','Dev','SentB','SentP','DroppedP','OverlimitsB','Requeues','BackB','BackP']
dev_keys = []
rootNo_keys = []
prev_t = 0
first_time =True

def tcshow (e):
    e.wait()
    e.clear()
    #tclock=threading.Lock()
    tclock = myGlobal.tclock
    idx = myGlobal.idx
    global prev_t
    curr_t =time.time()
    delta_t = curr_t-prev_t
    prev_t = curr_t
    del dev_keys[:]
    tccmd = "tc -s qdisc show"
    result = subprocess.check_output(tccmd,shell=True)
    parse_result = re.compile(r'qdisc\s*[a-zA-Z_]+\s+([0-9]+):\sdev\s([a-zA-Z0-9-]+)\s[a-zA-Z0-9_.:\s]+Sent\s([\d]+)\sbytes\s([\d]+)\spkt\s\(dropped\s([\d]+),\soverlimits\s([\d]+)\srequeues\s([\d]+)\)\s*backlog\s([\d]+)b+\s([\d]+)p')
    matches_d = parse_result.findall(result)
    #Hash Table
    entry = [dict(zip(entry_keys,row)) for row in matches_d]
    time_dict={'delta_t': delta_t}
    for item in entry:
    	#print item
		item.update(time_dict)
		dev_keys.append(item['Dev'])
#    	if not item['RootNo'] in RootNo_keys
#    		 RootNo_keys.append(item['Dev'])
    current_dict = {idx : dict(zip(dev_keys,entry))}
    tclock.acquire()
    tc_dict.update(current_dict)
    if len(tc_dict) > MAX_BUF:
        del tc_dict[idx-MAX_BUF]
#    if shared_Q.empty():
#        shared_Q.put(idx)
#        shared_Q.put(tc_dict)
#    else:
#        shared_Q.get()
#        if shared_Q.empty():
#        	shared_Q.put(idx)
#        	shared_Q.put(tc_dict)
#        else:
#            shared_Q.get()
#            shared_Q.put(idx)
#            shared_Q.put(tc_dict)
    idx +=1
    myGlobal.idx=idx
    tclock.release()

    #idx +=1
class TControl(threading.Thread):
	def __init__(self,e,counter):
		super(TControl, self).__init__()
		self.keeprunning = counter
		self.initial = counter
		self.event = e
	def run(self):
		try:
			while self.keeprunning > 0:
				tcshow(self.event)
				self.keeprunning-=1
		except KeyboardInterrupt:
			print "stoptimer"
			self.stop()
	def stop(self):			
		self.keeprunning = 0
	def reset(self):
		self.keeprunning = self.initial
		sleep = False

if __name__ == '__main__':
	e = threading.Event()
	counter = 200
	t1 = TControl(e,counter)
	t2 = Timer1(e,0.05,counter)
	t1.daemon = True
	t1.start()
	t2.start()