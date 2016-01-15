import sys


from models.db import db

import logging
logger = logging.getLogger(__name__)



def exec_server():
    logger.info("Starting")


    db.create_all()
    logger.info("Created database")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(exec_server())