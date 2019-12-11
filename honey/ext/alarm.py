"""
Cement alarm extension module.
"""

import signal
import time, threading
from cement.core.interface import minimal_logger

logger = minimal_logger(namespace='honey', debug=True)

def alarm_handler(app, signum, frame):
    if signum == signal.SIGALRM:
        app.log.error(app.alarm.msg)


class AlarmManager(threading.Thread):
    """
    https://stackoverflow.com/a/8420498/1493069
    A very simple thread that merely blocks for :attr:`interval` and sets a
    :class:`threading.Event` when the :attr:`interval` has elapsed. It then waits
    for the caller to unset this event before looping again.

    Example use::

        t = Ticker(1.0) # make a ticker
        t.start() # start the ticker in a new thread
        try:
          while t.evt.wait(): # hang out til the time has elapsed
            t.evt.clear() # tell the ticker to loop again
            print time.time(), "FIRING!"
        except:
          t.stop() # tell the thread to stop
          t.join() # wait til the thread actually dies

    """
    # SIGALRM based timing proved to be unreliable on various python installs,
    # so we use a simple thread that blocks on sleep and sets a threading.Event
    # when the timer expires, it does this forever.
    def __init__(self, *args, **kw):
        super(AlarmManager, self).__init__(*args, **kw)
        self.interval = None
        for arg in args:
            if arg == "interval":
                self.interval = arg
        self.evt = threading.Event()
        self.evt.clear()
        self.should_run = threading.Event()
        self.should_run.set()
        self.msg = None

    def set(self, time, msg):
        """
        Set the application alarm to ``time`` seconds.  If the time is
        exceeded ``alarm`` is raised.
        Args:
            time (int): The time in seconds to set the alarm to.
            msg (str): The message to display if the alarm is triggered.
        """

        logger.debug('setting application alarm for %s seconds' % time)
        self.msg = msg
        self.interval = int(time)
        self.start()

    def stop(self):
        """Stop the this thread. You probably want to call :meth:`join` immediately
        afterwards
        """
        self.should_run.clear()

    def consume(self):
        was_set = self.evt.is_set()
        if was_set:
            self.evt.clear()
        return was_set

    def run(self):
        """The internal main method of this thread. Block for :attr:`interval`
        seconds before setting :attr:`Ticker.evt`

        .. warning::
          Do not call this directly!  Instead call :meth:`start`.
        """
        while self.should_run.is_set():
            time.sleep(self.interval)
            self.evt.set()


def load(app):
    """app.catch_signal is probably going to break stuff"""
    # app.catch_signal(signal.SIGALRM)
    app.extend('alarm', AlarmManager())
    app.hook.register('signal', alarm_handler)