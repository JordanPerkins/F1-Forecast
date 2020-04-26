""" Sets up the application with the Pywsgi web server, which
    is required to handle concurrent requests. """
import logging
from gevent.pywsgi import WSGIServer
from .app import application

PORT = 80

logging.info("Application starting on port %i", PORT)

http_server = WSGIServer(('0.0.0.0', PORT), application)
http_server.serve_forever()
