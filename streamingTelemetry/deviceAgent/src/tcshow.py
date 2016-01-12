#!/bin/python
import os,re
import time
import subprocess
import threading
import Queue
from myGlobal import myGlobal
from myGlobal import round_sigfigs as rnd
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


def tcshow ():
    '''
    This function handles a pulling event received from the timer
    It wakes up every 50ms (sampling time),collect all the data of all interfaces
    and store them in tc_dict
    '''
    # grab the locker and idx
    tclock = myGlobal.tclock
    idx = myGlobal.idx
    
    # calculate delta_t
    global prev_t
    entry = []
    curr_t =time.time()
    delta_t = curr_t-prev_t
    prev_t = curr_t
    print delta_t
    #Available interfaces (devices), e.g. eth1, eth0
    dev_keys = []
    #Available child interfaces (devices)
    netem_dev_keys = []
    
    #parse tc show root result
    tccmd = "tc -s qdisc show"
    #start = time.time()
    result = subprocess.check_output(tccmd,shell=True)
    #end = time.time()
    #print(end - start)
    #start = time.time()
    #print result
    #print result.split()
    parse_result = re.compile(r'qdisc\s*[a-zA-Z_]+\s+([0-9]+):\sdev\s([a-zA-Z0-9-]+)\sroot\s[a-zA-Z0-9_.:\s]+Sent\s([\d]+)\sbytes\s([\d]+)\spkt\s\(dropped\s([\d]+),\soverlimits\s([\d]+)\srequeues\s([\d]+)\)\s*backlog\s([\d]+)b+\s([\d]+)p')
    matches_d = parse_result.findall(result)
    entry = [dict(zip(entry_keys,row)) for row in matches_d]
    #end = time.time()
    #print(end - start)
    #parse tc show parent result
    #print entry
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
    #tc_dict.update({idx : dict(zip(dev_keys,entry))})
    tc_dict.update(dict(zip(dev_keys,entry)))
    #print tc_dict[idx]['s1-eth2']
    #print tc_dict
    if len(tc_dict) > MAX_BUF:
	#remove the out of boundary entry
        del tc_dict[idx-MAX_BUF]
    idx +=1
    myGlobal.idx=idx
    tclock.release()


def cal_stats(devs,timestamp):
    '''
    This function calculates bw and delay for requested entries:
          |<---requested entries range--->|
    ------|-------------------------------|---->t
        start                            idx
    And then it return a list of integrated available bandwidth and delay along the path
    for example,
    [1,0.0501,5,50] means [idx = 1, delta_t = 0.0501s, Available bandwidth=5Mbps(bottleneck), total delay = 50ms]
    total delay includes propagation delay as well as queueing delay.

    '''
    #print "index"
    #print idx
    #print "index-range"
    #print idx-entries_range
    #start = time.time()
        #list of one entry
    l=[]
    tcshow()
    #print tc_dict
    for dev in devs:

        #print tc_dict[dev]
        l.append(dev)
        l.append(rnd(float(tc_dict[dev]['delta_t']),3))
        l.append(int(tc_dict[dev]['BackB']))
        l.append(int(tc_dict[dev]['SentB']))

        if 'P_Delay' in tc_dict[dev]:
            l.append(rnd(float(tc_dict[dev]['P_Delay']), 3))
        else:
            l.append(rnd(float(0), 3))

    #link counter which indicates the current link index in link_cap

    #print j2k_stats
        #print entries_range 
    #end = time.time()
    #print(end - start)
    return l

class tc_asyc_worker(threading.Thread):
    '''
    A simple thread for controlling tcshow.
    This function is triggered by timer event
    '''
    def __init__(self,e,counter):
        super(tc_asyc_worker, self).__init__()
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
   devs = ['eth0']
   print cal_stats(devs,'now')
