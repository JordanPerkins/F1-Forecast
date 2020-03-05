from flask import Flask
from .race import race_prediction
from .qualifying import qualifying_prediction
from ..common.db import Database

# Intialise DB singleton
Database()

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

application = Flask(__name__)

application.add_url_rule('/race/<int:race_id>', None, race_prediction)
application.add_url_rule('/race', None, race_prediction)

application.add_url_rule('/qualifying/<int:race_id>', None, qualifying_prediction)
application.add_url_rule('/qualifying', None, qualifying_prediction)

application.add_url_rule('/', None, lambda: 'Ok')

if __name__ == '__main__':
    application.run(host="0.0.0.0")