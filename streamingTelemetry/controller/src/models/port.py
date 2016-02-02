import json

from db import db
from node import Node
import logging
logger = logging.getLogger(__name__)


class Port(db.Model):
    port_id = db.Column(db.String(80), unique=True, primary_key=True)
    port_name = db.Column(db.String(80))
    port_type = db.Column(db.String(20))
    node_id = db.Column(db.String(80), db.ForeignKey('node.node_id'))
    port_ip = db.Column(db.String(80))
    port_mac = db.Column(db.String(80))
    start_date = db.Column(db.String(20))
    update_date = db.Column(db.String(20))
    node = db.relationship('Node',
        backref=db.backref('ports', lazy='dynamic'))
    def __init__(self, port_id, port_name, port_type,
                 port_ip, port_mac, node, start_date, update_date):
        self.port_id = port_id
        self.port_name = port_name
        self.port_type = port_type
        self.port_ip = port_ip
        self.port_mac = port_mac
        self.node = node
        self.start_date = start_date
        self.update_date = update_date

    def __repr__(self):
        return '<Port :%r>' % (self.port_id)

    def to_json(self):
        logging.info("Jsonifying Object %s" % self)
        return {
                'port_id': self.port_id,
                'port_name': self.port_name,
                'port_type': self.port_type,
                'port_ip': self.port_ip,
                'port_mac': self.port_mac,
                'start_date': self.start_date,
                'update_date': self.update_date
                }