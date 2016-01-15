from models.db import db
from models.flow import Flow

num_rows_deleted = db.session.query(Flow).delete()
print num_rows_deleted
