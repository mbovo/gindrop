from __future__ import absolute_import, division, print_function
import logging
import signal
import sys

from gindrop import api
from gevent.wsgi import WSGIServer

logger = logging.getLogger(__name__)
http_server = WSGIServer((api.config.server, int(api.config.port)), api.app, log=logger)


def sig_handler(signum, stack):
    if signum in [1, 2, 3, 15]:
        logger.warning('Caught signal %s, exiting.', str(signum))
        http_server.stop(api.config.stop_timeout)
        sys.exit()
    else:
        logger.warning('Caught signal %s, ignoring.', str(signum))
    return stack


def set_sig_handler(funcname, avoid=['SIG_DFL', 'SIGSTOP', 'SIGKILL']):
    for i in [x for x in dir(signal) if x.startswith("SIG") and x not in avoid]:
        try:
            signum = getattr(signal, i)
            signal.signal(signum, funcname)
        except (OSError, RuntimeError, ValueError) as m:  # OSError for Python3, RuntimeError for 2
            logging.warning("Skipping {} {}".format(i, m))


def main():
    set_sig_handler(sig_handler)
    logger.info('Starting Listening on %s:%d', api.config.server, int(api.config.port))
    http_server.serve_forever()
