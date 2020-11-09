import sys
import time
import traceback
from multiprocessing import Lock

from blottertrax.applications.submissions import Submissions


class SubmissionDaemon:
    crash_timeout: int = 10

    def start(self, lock: Lock):
        try:
            Submissions(lock).run()

        except Exception:
            traceback.print_exc(file=sys.stdout)

            time.sleep(self.crash_timeout)

        self.start(lock)
