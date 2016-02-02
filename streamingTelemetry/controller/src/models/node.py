import json

from db import db

import logging
logger = logging.getLogger(__name__)


class Node(db.Model):
    node_id = db.Column(db.String(80), unique=True, primary_key=True)
    node_name = db.Column(db.String(80))
    node_type = db.Column(db.String(20))
    management_ip = db.Column(db.String(80))
    management_mac = db.Column(db.String(80))
    start_date = db.Column(db.String(20))
    update_date = db.Column(db.String(20))
    def __init__(self, node_id, node_name, node_type,
                 management_ip, management_mac, start_date, update_date):
        self.node_id = node_id
        self.node_name = node_name
        self.node_type = node_type
        self.management_ip = management_ip
        self.management_mac = management_mac
        self.start_date = start_date
        self.update_date = update_date

    def __repr__(self):
        return '<Node :%r>' % (self.node_id)

    def to_json(self):
        logging.info("Jsonifying Object %s" % self)
        return {'node_id': self.node_id,
                'node_name':self.node_name,
                'node_type':self.node_type,
                 'management_ip': self.management_ip,
                 'management_mac': self.management_mac,
                 'start_date': self.start_date,
                 'update_date': self.update_date
                }