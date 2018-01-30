from __future__ import absolute_import, division, print_function
import logging
import time
from gevent.wsgi import WSGIServer

from . import core, api

config = core.config


class Gindrop(object):

    def __init__(self):
        self._start = time.time()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._http_server = WSGIServer((config.server, int(config.port)), api.webapp, log=self.logger)
        self._stop = 0

    @property
    def config(self):
        return config

    @property
    def http_server(self):
        return self._http_server

    def stop(self):
        self._http_server.stop(config.stop_timeout)

    def run(self):
        self._stop = time.time()
        self.logger.info('Startup in ' + "{:1.5f}".format(self._stop - self._start) + "s")
        self.logger.info('Starting Listening on %s:%d', config.server, int(config.port))
        self._http_server.serve_forever()
