
import json


class MageException(Exception):
    http_code = 500
    error_number = 1000
    message = "GenericMageException"

    def __init__(self, detail=""):
        Exception.__init__(self)
        self._detail = detail
        self._error_type = type(self).__name__

    def get_response_json(self):
        response = dict()
        response['message'] = self.message
        response['detail'] = self._detail
        response['error_type'] = self._error_type
        response['error_number'] = self.error_number
        return json.dumps(response)

    def get_http_code(self):
        return int(self.http_code)



class UserException(MageException):
    http_code = 400
    error_number = 4001
    message = "A General User Error Occured"

class DBException(UserException):
    error_number = 4003
    message = "Unable to update the database"
    
class NoConnectedDevice(UserException):
    error_number = 4002
    message = "Unable to locate connected device"



class NotFound(UserException):
    error_number = 4004
    message = "Unable to find the results to request"


class NoConnectedBridge(UserException):
    error_number = 4005
    message = "Unable to reach your gateway"


class BadRequest(UserException):
    error_number = 4006
    message = "Unable to process request"


class ISPException(MageException):
    http_code = 500
    error_number = 5001
    message = "A General ISP Error Occured"


class InvalidCustomer(ISPException):
    error_number = 5002
    message = "ISP is missing the customer_id"


class UnableToConnect(ISPException):
    error_number = 5003
    message = "We are unable to connect to your ISP"
