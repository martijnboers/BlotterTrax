from multiprocessing import Process, Lock


from blottertrax.daemons.modmail_daemon import ModMailDaemon
from blottertrax.daemons.submissions_daemon import SubmissionDaemon


def daemon():
    lock = Lock()

    Process(target=ModMailDaemon().start, args=(lock,)).start()
    Process(target=SubmissionDaemon().start, args=(lock,)).start()


if __name__ == '__main__':
    daemon()
