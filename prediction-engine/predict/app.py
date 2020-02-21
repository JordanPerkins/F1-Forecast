from flask import Flask
from .race import race_prediction

application = Flask(__name__)

application.add_url_rule('/race', None, race_prediction)

application.add_url_rule('/', None, lambda: 'Ok')

if __name__ == '__main__':
    application.run(host="0.0.0.0")