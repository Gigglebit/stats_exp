# multithreading
import threading
import time
# ntp related
import ntplib
from datetime import datetime
# server related
import json
from flask import Flask, request, jsonify
import urllib2

# local library
from tcshow import cal_stats
from printout import printout
from ThreadedUDPClient import client
from agent import Agent
import subprocess
import logging
logger = logging.getLogger(__name__)
CONTROLLER_IP = "10.1.1.2"
app = Flask(__name__)
th = None
@app.route('/')
def hello_world():
	get_ntp_time()
	e = threading.Event()
	ip, port, message = "10.1.1.2", 9999, 'Hello World'
	interval = 1
	counter = 20
	t1 = Agent(e,interval,counter,ip,port,message)
	t1.start()
	return message
@app.route('/api/ag/v1/monitor', methods=['GET'])
def monitor():
	global th
	th.start()
	return "Monitoring started"

@app.route('/api/ag/v1/config', methods=['GET', 'POST'])
def config():
	if request.method == 'POST':
		logger.info('setup configuration')
		json = request.json
		print request
		print json
		interval = int(json['interval'])
		duration = int(json['duration'])
		ip = json['controllerIp']
		port = int(json['controllerPort'])
		e = threading.Event()
		message = 'Monitoring'
		global th
		th = Agent(e,interval,duration,ip,port,message)
	else:
		logger.info('get_config')
	return 'Config!'
@app.route('/api/ag/v1/link_info', methods=['GET'])
def get_link_info():
	command = "ip neighbour"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	output = stdout.splitlines()
	link_dict = {}
	devs = []
	for line in output:
		newline = line.split()
		if newline[-1]=='REACHABLE' or newline[-1]=='DELAY':
			links = []
			subdict = {}
			if newline[2] in devs:
				subdict[newline[3]]=newline[4]
				subdict['ipAddress']=newline[0]
				link_dict[newline[2]].append(subdict)
			else:
				devs.append(newline[2])
				subdict[newline[3]]=newline[4]
				subdict['ipAddress']=newline[0]
				links.append(subdict)
				link_dict[newline[2]] = links

	print link_dict


	route_dict = {}
	command = "ip route"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	output = stdout.splitlines()
	devs = []
	for line in output:
		routes = []
		subdict = {}
		newline = line.split()
		if newline[0] == 'default':
			subdict['default']=newline[2]
			routes.append(subdict)
			route_dict[newline[-1]] = routes
			devs.append(newline[-1])
		else:
			if newline[2] in devs:
				subdict['src']=newline[-1]
				subdict['dst']=newline[0]
				route_dict[newline[2]].append(subdict)
			else:
				subdict['src']=newline[-1]
				subdict['dst']=newline[0]
				routes.append(subdict)
				route_dict[newline[2]] = routes
	print route_dict
	ret = {}
	ret['routes']=route_dict
	ret['links']=link_dict
	return jsonify(response = ret) 

def get_ntp_time():
	c = ntplib.NTPClient()
	response = c.request(CONTROLLER_IP, version=3)
	t = datetime.fromtimestamp(response.orig_time)
	return t.strftime("%a %b %d %H:%M:%S.%f")

def scan_ports():
	pass
class interpreter():
	def digestconfig(): 
		pass
	def checkconfig():
		pass
class datapusher():
	def sendtelemetrydata():
		pass


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	app.run(debug=True, host='0.0.0.0')