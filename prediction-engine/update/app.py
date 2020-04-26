""" The application for handling DB updating and model training. """

import logging
import traceback
from flask import Flask, abort
from ..common.db import Database
from .update_database import check_for_database_updates
from ..common.race import train as train_race
from ..common.qualifying import train as train_qualifying

# Intialise DB singleton
Database()

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

def run_update():
    """ Update the datbase and hthen models. """
    try:
        check_for_database_updates()
        logging.info("Database updating completed, now retraining models")
        logging.info("Training race")
        train_race(num_epochs=10)
        logging.info("Training qualifying")
        train_qualifying(num_epochs=10)
        logging.info("Model training completed, now pausing until next run")
        return 'Done'
    except Exception as err:
        logging.error('An error occurred during the update process: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")

application = Flask(__name__)

application.add_url_rule('/', None, run_update, methods=['POST'])
application.add_url_rule('/scheduled', None, run_update, methods=['POST'])
