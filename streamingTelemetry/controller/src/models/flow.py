import json

from db import db

import logging
logger = logging.getLogger(__name__)


class Flow(db.Model):
    flowId = db.Column(db.String(80), unique=True, primary_key=True)
    srcIp = db.Column(db.String(20))
    dstIp = db.Column(db.String(20))
    srcPort = db.Column(db.String(20))
    dstPort = db.Column(db.String(20))
    proto = db.Column(db.String(20))
    appType = db.Column(db.String(20))
    startDate = db.Column(db.String(20))
    updateDate = db.Column(db.String(20))
    def __init__(self, flowId, srcIp, dstIp,
                 srcPort, dstPort, proto, appType, startDate, updateDate):
        self.flowId = flowId
        self.srcIp = srcIp
        self.dstIp = dstIp
        self.srcPort = srcPort
        self.dstPort = dstPort
        self.proto = proto
        self.appType = appType
        self.startDate = startDate
        self.updateDate = updateDate

    def __repr__(self):
        return '<Flow :%r>' % (self.flowId)

    def to_json(self):
        logging.info("Jsonifying Object %s" % self)
        return {'flowId': self.flowId,
                 'srcIp': self.srcIp,
                 'dstIp': self.dstIp,
                 'srcPort': self.srcPort,
                 'dstPort': self.dstPort,
                 'proto': self.proto,
                 'appType':self.appType,
                 'startDate': self.startDate,
                 'updateDate': self.updateDate
                }
