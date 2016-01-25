from models.db import db

from models.flow import Flow
from time import gmtime, strftime
import uuid
flowId=str(uuid.uuid4())
now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
f1 = Flow(flowId,'192.168.0.2','192.168.0.3','12345','10005','UDP','j2k',now ,'13/01/2016')
flowId=str(uuid.uuid4())
f2 = Flow(flowId,'192.168.0.4','192.168.0.6','12345','10005','UDP','j2k',now ,'13/01/2016')
flowId=str(uuid.uuid4())
f3 = Flow(flowId,'192.168.0.8','192.168.0.9','12345','10005','UDP','j2k',now ,'13/01/2016')

db.session.add(f1)
db.session.add(f2)
db.session.add(f3)
db.session.commit()
