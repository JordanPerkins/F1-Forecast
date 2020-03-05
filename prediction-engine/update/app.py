from ..common.db import Database
from .update_database import check_for_database_updates
import logging
import traceback
from time import sleep

# Intialise DB singleton
Database()

def run_update():
    try:
        while True:
            check_for_database_updates()
            logging.info("Database updating completed, now retraining models")
            logging.info("Model training completed, now pausing for 1 hour")
            sleep(60 * 60)
    except Exception as e:
        logging.error('An error occurred during the update process: '+str(e))
        logging.debug(traceback.format_exc())


if __name__ == '__main__':
    run_update()