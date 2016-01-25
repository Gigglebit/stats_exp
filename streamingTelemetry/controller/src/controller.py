import json
import datetime
import pytest
import requests
from time import gmtime, strftime
import uuid
import subprocess
from mock import MagicMock
import grequests
from flask import jsonify
# database
from models.db import db
from models.flow import Flow
# exceptions
from mage_exceptions import NoConnectedDevice, \
    NoConnectedBridge, \
    UserException, \
    UnableToConnect, \
    DBException

from requests.exceptions import Timeout, \
    ConnectionError, \
    TooManyRedirects, \
    HTTPError

import logging
logger = logging.getLogger(__name__)
db.create_all()
class Controller(object):
    def __init__(self, hostname):
        assert hostname is not None
        assert hostname is not ''
        self.hostname = hostname
        self.port = 5000
        self.protocol = "http"
        self.markup = "json"
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}
        
    def _get_grequests(self, ipAddresses, endpoint):
        urls = []
        for ip in ipAddresses:
            self.hostname = ip
            urls.append(self._generate_url(endpoint))
        print urls 
        rs = (grequests.get(u) for u in urls)
        responses = grequests.map(rs,exception_handler=exception_handler)
        for response in responses:
            print response.content

    def _post_grequests(self, ipAddresses, endpoint, params):
        urls = []
        for ip in ipAddresses:
            self.hostname = ip
            urls.append(self._generate_url(endpoint))
        print urls 
        rs = (grequests.post(u, json=params) for u in urls)
        responses = grequests.map(rs,exception_handler=exception_handler)
        for response in responses:
            print response.content

    def _generate_url(self, endpoint):
        assert endpoint is not None
        assert endpoint is not ''

        url = "%s://%s:%s/api/ag/v1/%s" % (self.protocol,
                                    self.hostname,
                                    self.port,
                                    endpoint)

        return url

    def _process_error(self, response):
        logger.info("Processing HTTPError ....")

        error_dict = {
            400: UserException("Bad request 400"),
            404: UserException("Not found 404"),
            500: UserException("Internal Error 500"),
            501: UserException("Not implemented 501")
        }

        raise error_dict(response.status_code)

    def _get(self, endpoint):
        # data = None
        # return self._request('GET', endpoint, data)
        url = self._generate_url(endpoint)

        logger.debug(self.headers)
        logger.info(url)

        r = requests.get(url, headers=self.headers,timeout=1)
        logger.info("Response from Controller controller :  %s " % r)
        r.raise_for_status()

        logger.info(r)
        logger.info("response in _get: %s" % r.json())
        logger.debug(r.json())

        return r.json()

    def _post(self, endpoint, data):
        # return self._request('POST', endpoint, data)
        url = self._generate_url(endpoint)

        logger.debug(self.headers)
        logger.info(url)

        r = requests.post(url, headers=self.headers, data=json.dumps(data))
        r.raise_for_status()

        logger.info(r)
        logger.info(r.json())
        logger.debug(r.json())

        return r.json()

    def _put(self, endpoint, data):
        # return self._request('PUT', endpoint, data)
        url = self._generate_url(endpoint)
        return requests.put(url, headers=self.headers, data=data.json)

    def _delete(self, endpoint, data):
        # return self._request('DEL', endpoint, data)
        url = self._generate_url(endpoint)

        logger.debug(self.headers)
        logger.info(url)

        r = requests.delete(url, headers=self.headers, data=json.dumps(data))
        r.raise_for_status()

        logger.info(r)
        logger.info(r.json())
        logger.debug(r.json())

        return r.json()

    def _request(self, req_type, endpoint, data):
        print "Generic Arguments and parameters for each request."
        url = self._generate_url(endpoint)

        r = requests.Request(req_type,
                             url=url,
                             headers=self.headers,
                             data=data)

        r.prepare()

        # Do not remove. This is essential validation.
        try:
            r.raise_for_status()
        except (Timeout, TooManyRedirects, ConnectionError) as e:
            msg = "The controller Error: %s" % r.text
            logger.error(msg)

            raise UnableToConnect(msg)

        except HTTPError as e:
            logger.error(e)
            self._process_error(r)

        return r.json()
    ########
    # Scan Networks
    ########
    def scan_networks(self,ipAddresses):
        command = "nmap -sn %s"%ipAddresses
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.splitlines()
        hosts=output[-1].split()[5].split('(')[1]
        ips = []
        latencies = []
        for i in range(2,int(hosts)*2+2):
                if i%2==0:
                   ips.append(output[i].split()[-1])
                else:
                   latencies.append(output[i].split()[-2].split('(')[1])
        process.wait()
        print ips
        print latencies
        endpoint = 'link_info'
        self._get_grequests(ips, endpoint)
        return 'completed'
    ########
    # Flow registration 
    ########
    def register_flow(self,srcIp,dstIp,srcPort,dstPort,proto,appType):
        flowId = ""
        flowIdInDb = check_flow_existence_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType)
        if flowIdInDb=="":
            try:
            	flowId  = str(uuid.uuid4())
            	add_flow_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType,flowId)
            	# run this asynchronously find_the_path(srcIp,dstIp,srcPort,dstPort,proto)
            except:
            	msg = "The data cannot be inserted in the DB"
            	logger.error(msg)
            	raise DBException(msg)
        else:
        		msg = "The data exists in DB"
        		logger.error(msg)
        		flowId = flowIdInDb
        return flowId 
    def get_all_flows(self):
        flows = []
        flows = retrieve_all_flows_from_db()
        return flows
    def get_registered_flow_info(self, flowId):
    	flow = dict()
    	try:
    		flow = retrieve_flow_from_db(flowId)
    	except:
	    	msg = "The data cannot be retrieved from the DB"
	    	logger.error(msg)
	    	raise DBException(msg)
    	return flow
    def delete_all_flows(self):
        try:
            delete_all_flows_from_db()
        except:
            msg = "Deleting all data from the DB failed"
            logger.error(msg)
            raise DBException(msg)

    def delete_flow(self, flowId):
    	deletedFlowId = ""
    	try:
    		deletedFlowId = delete_flow_from_db(flowId)
    	except:
	    	msg = "The data cannot be deleted from the DB"
	    	logger.error(msg)
	    	raise DBException(msg)
    	return deletedFlowId
    #############################
    # Monitoring requests handler
    #############################
    def enable_flow_monitoring(self, flow_id, interval, duration, negotiation, direction):
        logger.info("enabling flow monitor to all the probes along the path")
        # nodes = self.get_the_path('flow_id')
        ipAddresses = ['10.1.1.3','10.1.1.4']
        endpoint = "config"
        params = {'interval':interval[0], 'duration':duration[0], 'controllerIp':'10.1.1.2', 'controllerPort':'9999'}
        self._post_grequests(ipAddresses, endpoint, params)
        endpoint = "monitor"

        self._get_grequests(ipAddresses, endpoint)

    	return "Enabled Flow Monitoring"
    def get_flow_monitoring_info(self, flow_id):
    	return ""
    def disable_flow_monitoring(self, flow_id):
    	return ""
    def get_the_path(self, flow_id):
        return ""


def exception_handler(request, exception):
    print "Request failed"

######################
# MockUp DB Operations
######################
def add_flow_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType,flowId):
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    update = now

    f = Flow(flowId,srcIp,dstIp,srcPort,dstPort,proto,appType,now,update)

    db.session.add(f)
    db.session.commit()
def check_flow_existence_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType):
    flowId = ""
    f=Flow.query.filter_by(srcIp=srcIp).filter_by(dstIp=dstIp).filter_by(srcPort=srcPort).filter_by(dstPort=dstPort).filter_by(proto=proto).filter_by(appType=appType).first()
    if f:
        flowId = f.to_json()['flowId']
    return flowId
def retrieve_flow_from_db(flowId):
    flow=dict()
    f = Flow.query.filter_by(flowId=flowId).first()
    if f:
        flow = f.to_json()
    return flow
def retrieve_all_flows_from_db():
    flows = []
    for raw_entry in Flow.query.all():
        entry = raw_entry.to_json()
        flows.append(entry)
    return flows
def delete_flow_from_db(flowId):
    f = Flow.query.filter_by(flowId=flowId).first()
    db.session.delete(f)
    db.session.commit()
    return flowId
def delete_all_flows_from_db():
    db.session.query(Flow).delete()
    db.session.commit()

class TestController(object):
    def test_controller_cannot_be_created_without_hostname(self):
        with pytest.raises(TypeError):
            Controller()
        with pytest.raises(AssertionError):
            Controller('')
        with pytest.raises(AssertionError):
            Controller(None)

    def test_controller_can_generate_url(self):
        fake_hostname = 'fake_hostname'
        cl = Controller(fake_hostname)
        with pytest.raises(TypeError):
            cl._generate_url()
        with pytest.raises(AssertionError):
            cl._generate_url(None)
        with pytest.raises(AssertionError):
            cl._generate_url('')

    def test_controller_wont_generate_url_without_endpoint(self):
        fake_hostname = 'fake_hostname'
        cl = Controller(fake_hostname)
        with pytest.raises(TypeError):
            cl._generate_url()
        with pytest.raises(AssertionError):
            cl._generate_url(None)
        with pytest.raises(AssertionError):
            cl._generate_url('')