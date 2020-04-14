""" Initialisation of the application, including declaration of the routes. """

import logging
from flask import Flask
from .predict import qualifying_prediction, race_prediction
from .info import (season_calendar, drivers_championship, constructors_championship,
                   race_results, qualifying_results)
from ..common.db import Database

# Intialise DB singleton
Database()

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

application = Flask(__name__)

application.add_url_rule('/predict/race/<int:race_id>', None, race_prediction)
application.add_url_rule('/predict/race', None, race_prediction)

application.add_url_rule('/predict/qualifying/<int:race_id>', None, qualifying_prediction)
application.add_url_rule('/predict/qualifying', None, qualifying_prediction)

application.add_url_rule('/info/calendar/<int:year>', None, season_calendar)
application.add_url_rule('/info/calendar', None, season_calendar)

application.add_url_rule('/info/championship/drivers/<int:year>', None, drivers_championship)
application.add_url_rule('/info/championship/drivers', None, drivers_championship)

application.add_url_rule('/info/championship/constructors/<int:year>', None, constructors_championship)
application.add_url_rule('/info/championship/constructors', None, constructors_championship)

application.add_url_rule('/info/results/race', None, race_results)
application.add_url_rule('/info/results/race/<int:race>', None, race_results)

application.add_url_rule('/info/results/qualifying', None, qualifying_results)
application.add_url_rule('/info/results/qualifying/<int:race>', None, qualifying_results)

application.add_url_rule('/', None, lambda: 'Ok')
