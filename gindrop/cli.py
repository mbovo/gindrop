from __future__ import absolute_import, division, print_function
import signal
import sys
from . import me

gin_app = me.Gindrop()


def sig_handler(signum, stack):
    if signum in [1, 2, 3, 15]:
        gin_app.logger.warning('Caught signal %s, exiting.', str(signum))
        gin_app.stop()
        sys.exit()
    else:
        gin_app.logger.warning('Ignoring signal %s.', str(signum))
    return stack


def set_sig_handler(funcname, avoid=['SIG_DFL', 'SIGSTOP', 'SIGKILL']):
    for i in [x for x in dir(signal) if x.startswith("SIG") and x not in avoid]:
        try:
            signum = getattr(signal, i)
            signal.signal(signum, funcname)
        except (OSError, RuntimeError, ValueError) as m:  # OSError for Python3, RuntimeError for 2
            gin_app.logger.warning("Skipping {} {}".format(i, m))


def main():
    set_sig_handler(sig_handler)
    gin_app.run()
