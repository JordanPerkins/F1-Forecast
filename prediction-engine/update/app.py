""" The application for handling DB updating and model training. """

import logging
import traceback
from time import sleep
from ..common.db import Database
from .update_database import check_for_database_updates
from ..common.race import train as train_race
from ..common.qualifying import train as train_qualifying

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
            logging.info("Training race")
            train_race()
            logging.info("Training qualifying")
            train_qualifying()
            logging.info("Model training completed, now pausing for 1 hour")
            sleep(60 * 60)
    except Exception as err:
        logging.error('An error occurred during the update process: %s', str(err))
        logging.debug(traceback.format_exc())


if __name__ == '__main__':
    run_update()
