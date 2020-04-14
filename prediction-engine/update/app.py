""" The application for handling DB updating and model training. """

import logging
import traceback
from time import sleep
from ..common.db import Database
from .update_database import check_for_database_updates
from .race_model import update_race_model

# Intialise DB singleton
Database()

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

def run_update():
    """ Handles continuous updating. """
    try:
        while True:
            check_for_database_updates()
            logging.info("Database updating completed, now retraining models")
            update_race_model()
            logging.info("Model training completed, now pausing for 1 hour")
            sleep(60 * 60)
    except Exception as err:
        logging.error('An error occurred during the update process: %s', str(err))
        logging.debug(traceback.format_exc())


if __name__ == '__main__':
    run_update()
