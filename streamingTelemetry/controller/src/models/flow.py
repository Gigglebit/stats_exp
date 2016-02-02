import json

from db import db

import logging
logger = logging.getLogger(__name__)


class Flow(db.Model):
    flow_id = db.Column(db.String(80), unique=True, primary_key=True)
    src_ip = db.Column(db.String(20))
    dst_ip = db.Column(db.String(20))
    src_port = db.Column(db.String(20))
    dst_port = db.Column(db.String(20))
    proto = db.Column(db.String(20))
    app_type = db.Column(db.String(20))
    start_date = db.Column(db.String(20))
    update_date = db.Column(db.String(20))
    def __init__(self, flow_id, src_ip, dst_ip,
                 src_port, dst_port, proto, app_type, start_date, update_date):
        self.flow_id = flow_id
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.proto = proto
        self.app_type = app_type
        self.start_date = start_date
        self.update_date = update_date

    def __repr__(self):
        return '<Flow :%r>' % (self.flow_id)

    def to_json(self):
        logging.info("Jsonifying Object %s" % self)
        return {'flow_id': self.flow_id,
                 'src_ip': self.src_ip,
                 'dst_ip': self.dst_ip,
                 'src_port': self.src_port,
                 'dst_port': self.dst_port,
                 'proto': self.proto,
                 'app_type':self.app_type,
                 'start_date': self.start_date,
                 'update_date': self.update_date
                }
