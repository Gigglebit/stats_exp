#!/bin/python
import os,re
import time
import subprocess
import threading
import Queue
from myGlobal import myGlobal
from myGlobal import round_sigfigs as rnd
from bottle import route, run
from json import dumps
import datetime
import os.path
import json
#a monitor running indicator
monitor_run = False

#threads holder
threads = []

#a copy of tc_dict
tc_result = {}
def cal_bw_delay(entries_range,idx,intf,tc_result):
    '''
    This function calculates bw and delay for requested entries:
          |<---requested entries range--->|
    ------|-------------------------------|---->t
        start                            idx
    And then it return a list of integrated available bandwidth and delay along the intf
    for example,
    [1,0.0501,5,50] means [idx = 1, delta_t = 0.0501s, Available bandwidth=5Mbps(bottleneck), total delay = 50ms]
    total delay includes propagation delay as well as queueing delay.

    '''
    j2k_stats = []
    #print "index"
    #print idx
    #print "index-range"
    #print idx-entries_range

    for i in xrange(idx-entries_range+1,idx,1):
        #list of one entry
        l=[]
        #link counter which indicates the current link index in link_cap
        
        if (i-1) in tc_result:
            l.append(i)
            j = intf
            l.append(rnd(float(tc_result[i][j]['delta_t']),3))

            l.append(int(tc_result[i][j]['BackB']))
            l.append(int(tc_result[i][j]['SentB']) - int(tc_result[i-1][j]['SentB']))
            if 'P_Delay' in tc_result[i][j]:
                l.append(rnd(float(tc_result[i][j]['P_Delay']), 3))
            else:
                l.append(rnd(float(0), 3))   
            j2k_stats.append(l)
        else:
            pass
    #print j2k_stats
        #print entries_range 
    return j2k_stats

def resolve_idx(intf,earliest_idx,num_entries,idx,tc_result):
    '''
    The logic of the combination of earliest_idx and num_entries
    '''
    if num_entries >= MAX_BUF or num_entries >= idx or earliest_idx > idx or num_entries < 0 or earliest_idx < 0:
        #if anything is outbound return nothing
        return [" "]    

    if num_entries==0 and earliest_idx ==0: #if none of the earlist_idx and num_entries were specified 
        if idx-MAX_BUF>=0: #when the index is higher more than 100
            return cal_bw_delay(MAX_BUF-1,idx,intf,tc_result) #calculate with all available data           
        else:
            return cal_bw_delay(idx,idx,intf,tc_result)
    elif num_entries!=0 and earliest_idx ==0: #if num_entries is specified
        if idx-MAX_BUF>=0:
            return cal_bw_delay(num_entries,idx,intf,tc_result) #calculate with the last num_entries entries 
        else:
            return cal_bw_delay(num_entries,idx,intf,tc_result)
    elif num_entries==0 and earliest_idx !=0: #if earlist idx is specified
        if idx-MAX_BUF>=0:
            if earliest_idx < idx-MAX_BUF:
                return cal_bw_delay(MAX_BUF-1,idx,intf,tc_result)
            else:
                return cal_bw_delay(idx-earliest_idx,idx,intf,tc_result)
        else:
            return cal_bw_delay(idx-earliest_idx,idx,intf,tc_result) #calculate with data starting earliest_idx
    else: #if you specified both of them
        if idx-MAX_BUF>=0: 
            if idx-num_entries < earliest_idx:
                return cal_bw_delay(idx-earliest_idx,idx,intf,tc_result)
            else:
                return cal_bw_delay(num_entries,idx,intf,tc_result)
        else:
            if idx-num_entries < earliest_idx:
                return cal_bw_delay(idx-earliest_idx,idx,intf,tc_result)
            else:
                return cal_bw_delay(num_entries,idx,intf,tc_result)

def requestmanager(intf, earliest_idx,num_entries):

    #print myGlobal.idx
    if len(tc_dict)>0:

        tclock = myGlobal.tclock
        tclock.acquire()
        tc_result = tc_dict
        index = myGlobal.idx-1
        tclock.release()        
        l = resolve_idx(intf,earliest_idx,num_entries,index,tc_result)
        return l
    else:
        return [" "]
#from threading import *
############################
# This is a simple function for extracting useful info from tc -s qdisc show
# entries[]:
# Extracted columns include:
# 0 1 2 3 4 5 6 7 8 9
# idx RootNo. DevName Sent(Bytes) Sent(Packets) Dropped(Packets) Overlimits(Bytes) Requeues Backlog(Bytes) Backlog(Packets)
#
# Because linux tc may also show the child queue class, Parent, Queue Depth and Propagation Delay may also be considered
#
# RootNo is related to multiple Queues of an interface pls ignore at the current stage
#
############################
#Length of the stats collector moving window: maximaly holding 100 entries
MAX_BUF = 100

#This is the dict that holds all entries
tc_dict ={}

#Dictionary possible keys
entry_keys = ['RootNo','Dev','SentB','SentP','DroppedP','OverlimitsB','Requeues','BackB','BackP']

#Child queue possible keys
netem_keys = ['RootNo','Dev','Parent','Q_Depth','P_Delay','SentB','SentP','DroppedP','OverlimitsB','Requeues','BackB','BackP']

#Available interfaces (devices), e.g. eth1, eth0
#dev_keys = []

#Available child interfaces (devices)
#netem_dev_keys = []

#Time tracker
prev_t = 0


def tcshow (e):
    '''
    This function handles a pulling event received from the timer
    It wakes up every 50ms (sampling time),collect all the data of all interfaces
    and store them in tc_dict
    '''
    # wait until being waken up
    e.wait()
    e.clear()
    
    # grab the locker and idx
    tclock = myGlobal.tclock
    idx = myGlobal.idx
    
    # calculate delta_t
    global prev_t
    entry = []
    curr_t =time.time()
    delta_t = curr_t-prev_t
    prev_t = curr_t
    
    #Available interfaces (devices), e.g. eth1, eth0
    dev_keys = []
    #Available child interfaces (devices)
    netem_dev_keys = []
    
    #parse tc show root result
    tccmd = "tc -s qdisc show"
    result = subprocess.check_output(tccmd,shell=True)
    parse_result = re.compile(r'qdisc\s*[a-zA-Z_]+\s+([0-9]+):\sdev\s([a-zA-Z0-9-]+)\sroot\s[a-zA-Z0-9_.:\s]+Sent\s([\d]+)\sbytes\s([\d]+)\spkt\s\(dropped\s([\d]+),\soverlimits\s([\d]+)\srequeues\s([\d]+)\)\s*backlog\s([\d]+)b+\s([\d]+)p')
    matches_d = parse_result.findall(result)
    entry = [dict(zip(entry_keys,row)) for row in matches_d]
    #parse tc show parent result
    result2 = subprocess.check_output(tccmd,shell=True)
    #print result2
    parse_result2 = re.compile(r'qdisc\snetem\s+([0-9]+):\sdev\s([a-zA-Z0-9-]+)\sparent\s([0-9]+:[0-9]+)\slimit\s([0-9]+)\sdelay\s([0-9.]+)[mu]s[a-zA-Z0-9_.:\s]+Sent\s([\d]+)\sbytes\s([\d]+)\spkt\s\(dropped\s([\d]+),\soverlimits\s([\d]+)\srequeues\s([\d]+)\)\s*backlog\s([\dA-Z]+)b\s([\d]+)p')
    matches_d2 = parse_result2.findall(result2)
    netem_entry = [dict(zip(netem_keys,row)) for row in matches_d2]
    #print matches_d2
    #save everything into a tc_dict{idx:{dev1:{'RootNo':...},dev2:{'RootNo':...}}}
    for item in entry:
    	#print item
        for netem_item in netem_entry:
	    if netem_item['Dev']==item['Dev']:
		item.update({'P_Delay':netem_item['P_Delay']})
                t = netem_item['BackB']
                if t.endswith('K'):
		  t = t[0:len(t)-1] + "000"
		if t.endswith('M'):
                  t = t[0:len(t)-1] + "000000"
		item.update({'BackB':t}) 
        item.update({'delta_t': delta_t})
        dev_keys.append(item['Dev'])
    
    #lock tc_dict and update it
    tclock.acquire()
    tc_dict.update({idx : dict(zip(dev_keys,entry))})
    # print idx
    # print tc_dict[idx]
    # print "-----------"
    if len(tc_dict) > MAX_BUF:
	#remove the out of boundary entry
        del tc_dict[idx-MAX_BUF]
    idx +=1
    myGlobal.idx=idx
    tclock.release()


class Timer1(threading.Thread):
    def __init__(self,e,seconds,counter):
        super(Timer1, self).__init__()
        self.runTime = seconds
        self.keeprunning = counter
        self.initial = counter
        self.event = e
    def run(self):
        try:
            counter = 0
            while self.keeprunning > 0:
                self.event.set()
                time.sleep(self.runTime)
                if counter == 20:
                    #print self.keeprunning/20
                    counter = 0
                counter +=1
                self.keeprunning-=1
                

            print "Going to sleep"
            global monitor_run
            monitor_run = False
        except KeyboardInterrupt:
            print "stoptimer"
            self.stop()
    def stop(self):         
        self.keeprunning = 0
    def reset(self):
        self.keeprunning = self.initial
        sleep = False

class TControl(threading.Thread):
	'''
	A simple thread for controlling tcshow.
	This function is triggered by timer event
	'''
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

def start_monitor():
    '''
    create a thread for timer2 
    '''
    global monitor_run
    if not monitor_run:
        if len(threads)!=0:
            del threads[:]  
        e = threading.Event()
        counter = 1000
        t1 = TControl(e,counter)
        t1.setName('TControl')
        t2 = Timer1(e,0.05,counter)
        t2.setName('Timer1')
        t1.daemon = True
        threads.append(t1)
        threads.append(t2)
        t1.start()
        t2.start()
        monitor_run = True
    else:
        #print "----reset threads-----"
        #print threads
        threads[0].reset()
        threads[1].reset()

@route("/start",method='GET')
def get_started():
    start_monitor()
    return json.dumps({"response":"started monitoring"})

@route("/stats/<intf>/<earliest_idx>/<num_entries>",method='GET')
def get_stats(intf, earliest_idx, num_entries):
    jpip_stats = requestmanager(intf, int(earliest_idx),int(num_entries))
    result = jpip_stats
    return json.dumps({"response":result})




if __name__ == '__main__':
    # e = threading.Event()
    # counter = 200
    # t1 = TControl(e,counter)
    # t2 = Timer1(e,0.05,counter)
    # t1.daemon = True
    # t1.start()
    # t2.start()
    run(server='cherrypy',host='10.1.1.4', port=8080, debug=True)
