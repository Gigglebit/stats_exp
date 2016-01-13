import json
import datetime
from flask import Flask, request,jsonify

from controller import Controller
from mage_exceptions import MageException, BadRequest, InvalidCustomer

import logging
logger = logging.getLogger(__name__)

app = Flask(__name__.split('.')[0])
controller_id = 'winston'
controller = Controller(controller_id)

@app.route('/api/v1/register', methods=['POST','GET'])
def register_flow():
	"""
    register
    """

	response = None
	if request.method == 'POST':
		logger.info("Register a flow")
		json = request.json
		srcIp=json['srcIp']
		dstIp=json['dstIp']
		srcPort=json['srcPort']
		dstPort=json['dstPort']
		proto=json['proto']
		appType=json['appType']
		response = controller.register_flow(srcIp,dstIp,srcPort,dstPort,proto,appType)
		response = jsonify(flow_id=response)
	else:
		response = controller.get_all_flows()
		response = jsonify(response=response)
	return response

@app.route('/api/v1/register/<flow_id>', methods=['GET','DELETE'])
def flow_operations(flow_id):
	response = None
	if request.method == 'GET':
	    logger.info("Getting the flow:%s" %
	                (flow_id))
	    response = controller.get_registered_flow_info(flow_id)
	    response = jsonify(response=response)
	elif request.method == 'DELETE':
	    logger.info("Deleting the flow:%s" %
	                (flow_id))
	    response = controller.delete_flow(flow_id)
	    response = jsonify(flow_id=response,msg="the flow has been removed successfully")

	return response

@app.route('/api/v1/monitor/<flow_id>', methods=['POST', 'GET', 'DELETE'])
def monitor_flow(flow_id):
	"""
    Monitoring is to be done on the lan port
    """
	response = None
	if request.method == 'POST':
		logger.info("Enabling Path Monitoring For Registered Flow:%s" % 
				(flow_id))
		json = request.json
		interval = json['interval'],
		duration = json['duration'],
		negotiation = json['negotiation'],
		direction = json['direction']
		response = controller.enable_flow_monitoring(flow_id,
			interval,
			duration,
			negotiation,
			direction)

	elif request.method == 'GET':
	    logger.info("Getting Path Monitoring Info For Registered Flow:%s" %
	                (flow_id))
	    response = controller.get_flow_monitoring_info(flow_id)

	elif request.method == 'DELETE':
	    logger.info("Disabling Path Monitoring For Registered Flow:%s" %
	                (flow_id))
	    response = controller.disable_flow_monitoring(flow_id)

	return response

def run_server():
    app.run(debug=True, host='0.0.0.0', port=8080)
#
# ERROR HANDLING
#
@app.errorhandler(MageException)
def handle_invalid_request(error):

    response = error.get_response_json()
    status = error.get_http_code()
    return response, status

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_server()