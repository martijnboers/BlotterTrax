import time
from multiprocessing import Lock

from blottertrax.applications.submissions import Submissions
from blottertrax.logger import Logger


class SubmissionDaemon:
    crash_timeout: int = 10

    def __init__(self):
        self.logger = Logger()

    def start(self, lock: Lock):
        try:
            self.logger.info('Starting SubmissionDaemon')

            Submissions(lock).run()
        except Exception:
            self.logger.exception('SubmissionDaemon threw exception')

            time.sleep(self.crash_timeout)

        self.start(lock)
