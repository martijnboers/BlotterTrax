import sys
import time
import traceback

from blottertrax.applications.modmail import ModMail


class ModMailDaemon:
    crash_timeout: int = 10

    def start(self):
        try:
            ModMail().run()

        except Exception:
            traceback.print_exc(file=sys.stdout)

            time.sleep(self.crash_timeout)

        self.start()
