#!/bin/python
import os,re
import time
import subprocess
import threading
from tcshow import * 

monitor_run = False
threads = []
tc_result = {}

def cal_bw_delay(entries_range,idx,path,link_cap,tc_result):
	'''
	This function append reverse order entries into jpip_stats
	Tell me the range of entries
	and tell me the reversed order starting point
	for example, to generate the following output, entries_range = 4, entries_start = 100 
	100,t,bw
	 99,t,bw
	 98,t,bw
	 97,t,bw
	since our window only has 100 entries, 
	when the idx go above 100 always set entries_start=MAX_BUF 
	otherwise entries_start=idx
	'''
	j2k_stats = []
	# print "index"
	# print idx
	# print "index-range"
	# print idx-entries_range

	for i in xrange(idx,idx-entries_range+1,-1):
		l=[]
		b=[]
		delay_sum = 0
		link_ct = 0
		for j in path:
			delta_sentB=int(tc_result[i][j]['SentB'])-int(tc_result[i-1][j]['SentB'])
			delta_t = float(tc_result[i][j]['delta_t'])
			bw = delta_sentB/delta_t
			b.append(float(link_cap[link_ct])-bw)
			SentP = float(tc_result[i][j]['SentP'])
			if SentP!=0:
				Psize = float(tc_result[i][j]['SentB'])/float(tc_result[i][j]['SentP'])
			else:
				Psize = 1000	
			delay = int(tc_result[i][j]['BackP'])*Psize/float(link_cap[link_ct])
			delay_sum += delay
			link_ct+=1
		l.append(i)
		l.append(delta_t)
		l.append(min(b))
		l.append(delay_sum)
		j2k_stats.append(l)

	return j2k_stats

def resolve_idx(path,earliest_idx,num_entries,link_cap,idx,tc_result):
	'''
	The logic of the combination of earliest_idx and num_entries
	'''
	j2k_stats = []
	if num_entries >= MAX_BUF or num_entries >= idx or earliest_idx > idx or num_entries < 0 or earliest_idx < 0:
		j2k_stats.append(" ") #if anything is outbound return nothing
		return j2k_stats 	

	if num_entries==0 and earliest_idx ==0:
		if idx-MAX_BUF>=0:#when the moving window has 100 entries
			return cal_bw_delay(MAX_BUF-1,idx,path,link_cap,tc_result)			
		else:
			return cal_bw_delay(idx,idx,path,link_cap,tc_result)
	elif num_entries!=0 and earliest_idx ==0:
		if idx-MAX_BUF>=0:
			return cal_bw_delay(num_entries,idx,path,link_cap,tc_result)
		else:
			return cal_bw_delay(num_entries,idx,path,link_cap,tc_result)
	elif num_entries==0 and earliest_idx !=0:
		if idx-MAX_BUF>=0:
			if earliest_idx < idx-MAX_BUF:
				return cal_bw_delay(MAX_BUF-1,idx,path,link_cap,tc_result)
			else:
				return cal_bw_delay(idx-earliest_idx,idx,path,link_cap,tc_result)
		else:
			return cal_bw_delay(idx-earliest_idx,idx,path,link_cap,tc_result)
	else:
		if idx-MAX_BUF>=0:
			if idx-num_entries < earliest_idx:
				return cal_bw_delay(idx-earliest_idx,idx,path,link_cap,tc_result)
			else:
				return cal_bw_delay(num_entries,idx,path,link_cap,tc_result)
		else:
			if idx-num_entries < earliest_idx:
				return cal_bw_delay(idx-earliest_idx,idx,path,link_cap,tc_result)
			else:
				return cal_bw_delay(num_entries,idx,path,link_cap,tc_result)

def requestmanager(path,link_cap,earliest_idx,num_entries):
	if len(tc_dict)>0:
		if shared_Q.full():
			index = shared_Q.get()
			tc_result = shared_Q.get()
		else:
			return
		if shared_Q.empty():
			shared_Q.put(index)
			shared_Q.put(tc_result)

		l = resolve_idx(path,earliest_idx,num_entries,link_cap,index,tc_result)

		return l
	else:
		return [" "]

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
					print self.keeprunning/20
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

def start_monitor():
	'''
	create a thread for timer2 
	'''
	global monitor_run
	if not monitor_run:
		if len(threads)!=0:
			del threads[:]	
		e = threading.Event()
		counter = 200
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


if __name__ == '__main__':
	e = threading.Event()
	counter = 200
	t1 = TControl(e,counter)
	t2 = Timer1(e,0.05,counter)
	t1.start()
	t2.start()
	path = ["eth0","eth1"]
	earliest_idx = 0
	num_entries = 0
	tc_request(path)
