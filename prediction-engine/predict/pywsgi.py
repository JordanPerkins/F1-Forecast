from gevent.pywsgi import WSGIServer
from .app import application
import logging

logging.info("Application starting on port 5000");

http_server = WSGIServer(('0.0.0.0', 5000), application)
http_server.serve_forever()