import sys
import time
import traceback
from multiprocessing import Lock

from blottertrax.applications.modmail import ModMail


class ModMailDaemon:
    crash_timeout: int = 10

    def start(self, lock: Lock):
        try:
            ModMail(lock).run()

        except Exception:
            traceback.print_exc(file=sys.stdout)

            time.sleep(self.crash_timeout)

        self.start(lock)
