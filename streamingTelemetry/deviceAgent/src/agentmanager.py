# multithreading
import threading
import time
# ntp related
import ntplib
from datetime import datetime
# server related
from flask import Flask, request
import json
import urllib2

# local library
from tcshow import cal_stats
from printout import printout
from ThreadedUDPClient import client
CONTROLLER_IP = "10.1.1.2"
app = Flask(__name__)
@app.route('/')
def hello_world():
	getNTPtime()
	e = threading.Event()
	ip, port, message = "10.1.1.2", 9999, 'Hello World'
	interval = 1
	counter = 20
	t1 = agent(e,interval,counter,ip,port,message)
	t1.start()
	return message
@app.route('/config', methods=['GET', 'POST'])
def config():
	if request.method == 'POST':
		print ('set_config')
	else:
		print ('get_config')
	return 'Config!'

def getNTPtime():
	c = ntplib.NTPClient()
	response = c.request(CONTROLLER_IP, version=3)
	t = datetime.fromtimestamp(response.orig_time)
	return t.strftime("%a %b %d %H:%M:%S.%f")


class interpreter():
	def digestconfig(): 
		pass
	def checkconfig():
		pass
class datapusher():
	def sendtelemetrydata():
		pass



class agent(threading.Thread):
	'''
	A simple thread for controlling tcshow.
	This function is triggered by timer event
	'''
	def __init__(self,e,interval,counter,ip,port,message):
		super(agent, self).__init__()
		self.keeprunning = counter
		self.initial = counter
		self.runtime = interval
		self.event = e
		self.ip = ip
		self.port = port
		self.message = message
	def run(self):
		try:
			print getNTPtime();
			while self.keeprunning > 0:
				# start = time.time()
				msg = cal_stats(['eth0'],'now')
				client(self.ip,self.port, msg)
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



if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')