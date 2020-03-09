import os
import sqlite3


class Database:
    cursor = None
    sql = None

    def __init__(self):
        self.sql = sqlite3.connect('{}/../database/submissions.db'.format(os.path.dirname(os.path.realpath(__file__))))
        self.cursor = self.sql.cursor()

        self.cursor.execute('CREATE TABLE IF NOT EXISTS submissions(id TEXT)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS postindex on submissions(id)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS errorCausingSubmissions(id TEXT NOT NULL, permalink TEXT, url TEXT, postTitle TEXT, artist TEXT, songTitle TEXT, error TEXT)')

    def save_submission(self, submission):
        self.cursor.execute('INSERT INTO submissions VALUES(?)', [submission.id])
        self.sql.commit()

    def log_error_causing_submission(self, parsed, raw, error, save_submission = False):

        if save_submission is True:
            self.save_submission(raw) # Save it so we will skip it next time we parse.

        if parsed is not None:
            self.cursor.execute('INSERT INTO errorCausingSubmissions VALUES(?, ?, ?, ?, ?, ?, ?)', [raw.id, raw.permalink, parsed.url, raw.title, parsed.artist, parsed.track_title, error])
        else:
            self.cursor.execute('INSERT INTO errorCausingSubmissions VALUES(?, ?, ?, ?, ?, ?, ?)', [raw.id, raw.permalink, raw.url, raw.title, "", "", error])
        self.sql.commit()

    def known_submission(self, submission) -> bool:
        self.cursor.execute('SELECT id FROM submissions WHERE id == ?', [submission.id])

        return self.cursor.fetchone() is not None
