import os
import sqlite3
from multiprocessing import Lock

from praw.models import Submission

from blottertrax.value_objects.parsed_submission import ParsedSubmission


class Database:
    cursor = None
    sql = None
    lock: Lock = None

    def __init__(self, lock: Lock):
        self.lock = lock

        self.lock.acquire()
        self.sql = sqlite3.connect('{}/../database/database.db'.format(os.path.dirname(os.path.realpath(__file__))))
        self.cursor = self.sql.cursor()

        self.cursor.execute('CREATE TABLE IF NOT EXISTS submissions(id TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS modmail(id TEXT)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS postindex on submissions(id)')
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS errorCausingSubmissions(
                id TEXT NOT NULL,
                permalink TEXT,
                url TEXT,
                postTitle TEXT,
                artist TEXT,
                songTitle TEXT,
                error TEXT
            )
            '''
        )
        self.lock.release()

    def save_submission(self, submission: Submission):
        self.lock.acquire()
        self.cursor.execute('INSERT INTO submissions VALUES(?)', [submission.id])
        self.sql.commit()
        self.lock.release()

    def log_error_causing_submission(self, parsed: ParsedSubmission, raw: Submission, error):
        self.lock.acquire()
        if parsed.success is True:
            self.cursor.execute('INSERT INTO errorCausingSubmissions VALUES(?, ?, ?, ?, ?, ?, ?)',
                                [raw.id, raw.permalink, parsed.url, raw.title, parsed.artist, parsed.track_title,
                                 error])
        else:
            self.cursor.execute('INSERT INTO errorCausingSubmissions VALUES(?, ?, ?, ?, ?, ?, ?)',
                                [raw.id, raw.permalink, raw.url, raw.title, "", "", error])
        self.sql.commit()
        self.lock.release()

    def known_submission(self, submission: Submission) -> bool:
        self.cursor.execute('SELECT id FROM submissions WHERE id == ?', [submission.id])

        return self.cursor.fetchone() is not None

    def save_mod_mail(self, mail):
        self.lock.acquire()
        self.cursor.execute('INSERT INTO modmail VALUES(?)', [mail.id])
        self.sql.commit()
        self.lock.release()

    def known_mod_mail(self, mail) -> bool:
        self.cursor.execute('select id from modmail where id == ?', [mail.id])
        return self.cursor.fetchone() is not None
