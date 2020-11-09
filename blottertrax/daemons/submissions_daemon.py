import sys
import time
import traceback

from blottertrax.applications.submissions import Submissions


class SubmissionDaemon:
    crash_timeout: int = 10

    def start(self):
        try:
            Submissions().run()

        except Exception:
            traceback.print_exc(file=sys.stdout)

            time.sleep(self.crash_timeout)

        self.start()
