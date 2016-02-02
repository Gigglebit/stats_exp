from models.db import db
from datetime import datetime
from models.flow import Flow
from models.node import Node
from models.port import Port 
from time import gmtime, strftime
import uuid
db.create_all()
flow_id=str(uuid.uuid4())

now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
f1 = Flow(flow_id,'192.168.0.2','192.168.0.3','12345','10005','UDP','j2k',now ,'13/01/2016')
flow_id=str(uuid.uuid4())
f2 = Flow(flow_id,'192.168.0.4','192.168.0.6','12345','10005','UDP','j2k',now ,'13/01/2016')
flow_id=str(uuid.uuid4())
f3 = Flow(flow_id,'192.168.0.8','192.168.0.9','12345','10005','UDP','j2k',now ,'13/01/2016')

node_id=str(uuid.uuid4())
node_name='CumulusNetworks'
node_type='Switch'
management_ip='192.168.0.2'
management_mac='AA:BB:CC:DD:EE:FF'

nd= Node(node_id, node_name, node_type,
                 management_ip, management_mac, now, '13/01/2016')


port_id=str(uuid.uuid4())
port_name='eth1'
port_type='ethernet'
port_ip='10.1.1.2'
port_mac='CC:DD:EF:23:32:1B'

p = Port(port_id, port_name, port_type,
                 port_ip, port_mac, nd, now, '13/01/2016')



db.session.add(f1)
db.session.add(f2)
db.session.add(f3)
db.session.add(nd)
db.session.add(p)
db.session.commit()
