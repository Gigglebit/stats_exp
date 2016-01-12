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
    UnableToConnect

from requests.exceptions import Timeout, \
    ConnectionError, \
    TooManyRedirects, \
    HTTPError

import logging
logger = logging.getLogger(__name__)

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
    def register_flow(self, srcIp,dstIp,srcPort,dstPort,proto,appType):
    	flow_id = str(uuid.uuid4())
    	return flow_id


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