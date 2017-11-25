from __future__ import absolute_import, division, print_function
import signal
import sys
from . import me

app = me.Gindrop()


def sig_handler(signum, stack):
    if signum in [1, 2, 3, 15]:
        app.logger.warning('Caught signal %s, exiting.', str(signum))
        app.stop()
        sys.exit()
    else:
        app.logger.warning('Ignoring signal %s.', str(signum))
    return stack


def set_sig_handler(funcname, avoid=['SIG_DFL', 'SIGSTOP', 'SIGKILL']):
    for i in [x for x in dir(signal) if x.startswith("SIG") and x not in avoid]:
        try:
            signum = getattr(signal, i)
            signal.signal(signum, funcname)
        except (OSError, RuntimeError, ValueError) as m:  # OSError for Python3, RuntimeError for 2
            app.logger.warning("Skipping {} {}".format(i, m))


def main():
    set_sig_handler(sig_handler)
    app.run()
