import json
import datetime
import pytest
import requests
import time
import uuid
from mock import MagicMock

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
db = dict()
db['flowTable']=[]
class Controller(object):
    def __init__(self, hostname):
        assert hostname is not None
        assert hostname is not ''
        self.hostname = hostname
        self.port = 8080
        self.protocol = "http"
        self.markup = "json"
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}

    def _generate_url(self, endpoint):
        assert endpoint is not None
        assert endpoint is not ''

        url = "%s://%s:%s/wm/%s" % (self.protocol,
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

        r = requests.get(url, headers=self.headers)
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
    # Flow registration 
    ########
    def register_flow(self,srcIp,dstIp,srcPort,dstPort,proto,appType):
		flowId = ""
		flowIdInDb = check_flow_existence_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType)
		if flowIdInDb=="":
			try:
				flowId  = str(uuid.uuid4())
				update_flow_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType,flowId)
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
		return db
    def get_registered_flow_info(self, flowId):
    	flow = dict()
    	try:
    		flow = retrieve_flow_from_db(flowId)
    	except:
	    	msg = "The data cannot be retrieved from the DB"
	    	logger.error(msg)
	    	raise DBException(msg)
    	return flow

    def delete_flow(self, flowId):
    	deletedFlowId = ""
    	try:
    		deletedFlowId = delete_flow_from_db(flowId)
    	except:
	    	msg = "The data cannot be retrieved from the DB"
	    	logger.error(msg)
	    	raise DBException(msg)
    	return deletedFlowId
    #############################
    # Monitoring requests handler
    #############################
    def enable_flow_monitoring(self, flow_id, interval, duration, negotiation, direction):
    	logger.info("enabling flow monitor to all the probes along the path")
    	# get_the_path('flow_id')
    	# endpoint = "/monitor/%s/"
    	# for node in nodes:
    	#     self._generate_url(node['ipAddress'],endpoint)

    	return ""
    def get_flow_monitoring_info(self, flow_id):
    	return ""
    def disable_flow_monitoring(self, flow_id):
    	return ""

######################
# MockUp DB Operations
######################
def update_flow_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType,flow_id):
	db['flowTable'].append({
			"srcIp":srcIp,
			"dstIp":dstIp,
			"srcPort":srcPort,
			"dstPort":dstPort,
			"proto":proto,
			"appType":appType,
			"flowId":flow_id,
	})
def check_flow_existence_in_db(srcIp,dstIp,srcPort,dstPort,proto,appType):
	flowId = ""
	for entry in db['flowTable']:
		if (entry['srcIp']==srcIp and  entry['dstIp']==dstIp and  entry['srcPort']==srcPort and entry['dstPort']==dstPort and entry['proto']==proto and entry['appType']==appType):
			return entry['flowId']
	return flowId
def retrieve_flow_from_db(flowId):
	flow = dict()
	for entry in db['flowTable']:
		if entry['flowId']==flowId:
			flow = entry
	return flow
def delete_flow_from_db(flowId):
	deletedFlowId = ""
	for entry in db['flowTable']:
		if entry['flowId']==flowId:
			deletedFlowId = flowId
			db['flowTable'].remove(entry)
	return deletedFlowId

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