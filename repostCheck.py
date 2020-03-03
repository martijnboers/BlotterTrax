import sqlite3


class RepostCheck:
    cursor = None
    sql = None

    def __init__(self):
        self.sql = sqlite3.connect('database/repost.db')
        self.cursor = self.sql.cursor()

        self.cursor.execute('CREATE TABLE IF NOT EXISTS artistSubmission(artist TEXT UNIQUE NOT NULL, postTime REAL NOT NULL, repeatCount INT NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS songSubmission(artistSong TEXT UNIQUE NOT NULL, postTime REAL NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS idStamped(postID TEXT UNIQUE NOT NULL, postTime REAL NOT NULL)')
        
        self.cursor.execute('SELECT * FROM artistSubmission')
    
    def new_entry(self, artistName, songName, currTime, postID):
        self.cursor.execute('INSERT OR IGNORE INTO artistSubmission VALUES(?, ?, ?)', [artistName, currTime, 0])
        self.cursor.execute('INSERT OR IGNORE INTO songSubmission VALUES(?, ?)', [songName + '--||' + artistName, currTime])
        self.cursor.execute('INSERT OR IGNORE INTO idStamped VALUES(?, ?)', [postID, currTime])
        self.sql.commit()
    
    def get_artist_timestamp(self, artistName):
        self.cursor.execute('SELECT postTime, repeatCount FROM artistSubmission WHERE artist == ?', [artistName])

        return self.cursor.fetchone()
    
    def replace_entry(self, artistName, songName, currTime, postID):
        self.cursor.execute('UPDATE artistSubmission SET postTime=? WHERE artist == ?', [currTime, artistName])
        self.cursor.execute('INSERT OR REPLACE INTO songSubmission VALUES(?, ?)', [songName + '--||' + artistName, currTime])
        self.cursor.execute('INSERT OR IGNORE INTO idStamped VALUES(?, ?)', [postID, currTime])
        self.sql.commit()
    
    def search_song(self, artistName, songName):
        self.cursor.execute('SELECT postTime FROM songSubmission WHERE artistSong == ?', [songName + '--||' + artistName])

        return self.cursor.fetchone()
    
    def get_old_submissions(self, currTime):
        self.cursor.execute('SELECT postID FROM idStamped WHERE postTime < ?', [currTime - 252000])
        idList = self.cursor.fetchall()
        
        self.cursor.execute('DELETE FROM idStamped WHERE postTime < ?', [currTime - 252000])
        self.sql.commit()
        
        return idList
    
    def add_count(self, artistName):
        self.cursor.execute('SELECT * FROM artistSubmission WHERE artist == ?', [artistName])
        self.cursor.execute('UPDATE artistSubmission SET repeatCount = repeatCount + 1 WHERE artist == ?', [artistName])
        self.sql.commit()
        self.cursor.execute('SELECT * FROM artistSubmission WHERE artist == ?', [artistName])