from flask import Flask
from .predict import qualifying_prediction, race_prediction
from .info import *
from ..common.db import Database
import logging

# Intialise DB singleton
Database()

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

application = Flask(__name__)

application.add_url_rule('/predict/race/<int:race_id>', None, race_prediction)
application.add_url_rule('/predict/race', None, race_prediction)

application.add_url_rule('/predict/qualifying/<int:race_id>', None, qualifying_prediction)
application.add_url_rule('/predict/qualifying', None, qualifying_prediction)

application.add_url_rule('/info/calendar/<int:year>', None, calendar)
application.add_url_rule('/info/calendar', None, calendar)

application.add_url_rule('/', None, lambda: 'Ok')

if __name__ == '__main__':
    application.run(host="0.0.0.0")