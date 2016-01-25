# multithreading
import threading
import time
# ntp related
import ntplib
from datetime import datetime
# customised
from tcshow import cal_stats
from ThreadedUDPClient import client
class Agent(threading.Thread):
	'''
	A simple thread for controlling tcshow.
	This function is triggered by timer event
	'''
	def __init__(self,e,interval,counter,ip,port,message):
		super(Agent, self).__init__()
		self.keeprunning = counter
		self.initial = counter
		self.runtime = interval
		self.event = e
		self.ip = ip
		self.port = port
		self.message = message
	def run(self):
		try:
			while self.keeprunning > 0:
				# start = time.time()
				msg = cal_stats(['eth0'],'now')
				print self.message
				print self.ip
				print self.port
				print msg
				print self.initial
				client(self.ip, self.port, msg)
				# end = time.time()
				# print(end - start)
				self.keeprunning-=1
				time.sleep(self.runtime)
		except KeyboardInterrupt:
			print "stoptimer"
			self.stop()
	def stop(self):			
		self.keeprunning = 0
	def reset(self):
		self.keeprunning = self.initial
		sleep = False