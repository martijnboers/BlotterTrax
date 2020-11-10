import time
from multiprocessing import Lock

from blottertrax.applications.modmail import ModMail
from blottertrax.logger import Logger


class ModMailDaemon:
    crash_timeout: int = 10

    def __init__(self):
        self.logger = Logger()

    def start(self, lock: Lock):
        try:
            self.logger.info('Starting ModMailDaemon daemon')

            ModMail(lock).run()
        except Exception:
            self.logger.exception('ModMailDaemon threw exception')

            time.sleep(self.crash_timeout)

        self.start(lock)
