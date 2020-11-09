import multiprocessing

from blottertrax.daemons.modmail_daemon import ModMailDaemon
from blottertrax.daemons.submissions_daemon import SubmissionDaemon


def daemon():
    mod_mail = multiprocessing.Process(target=ModMailDaemon().start)
    mod_mail.start()

    submissions = multiprocessing.Process(target=SubmissionDaemon().start)
    submissions.start()


if __name__ == '__main__':
    daemon()
