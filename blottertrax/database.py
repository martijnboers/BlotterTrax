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

    def save_submission(self, submission):
        self.cursor.execute('INSERT INTO submissions VALUES(?)', [submission.id])
        self.sql.commit()

    def known_submission(self, submission):
        self.cursor.execute('SELECT id FROM submissions WHERE id == ?', [submission.id])

        return self.cursor.fetchone() is not None
