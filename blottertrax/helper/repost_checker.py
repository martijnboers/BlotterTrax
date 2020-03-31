import sqlite3


class RepostChecker:
    cursor = None
    sql = None

    @classmethod
    def __init__(self):
        self.sql = sqlite3.connect('{}/../{}/../database/repost.db')
        self.cursor = self.sql.cursor()
    
        self.cursor.execute('CREATE TABLE IF NOT EXISTS artistSubmission(artist TEXT UNIQUE NOT NULL, postTime REAL NOT NULL, repeatCount INT NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS songSubmission(artistSong TEXT UNIQUE NOT NULL, postTime REAL NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS idStamped(postID TEXT UNIQUE NOT NULL, postTime REAL NOT NULL)')
    
    @classmethod
    def new_entry(self, artist_name, song_name, curr_time, post_id):
        self.cursor.execute('INSERT OR IGNORE INTO artistSubmission VALUES(?, ?, ?)', [artist_name, curr_time, 0])
        self.cursor.execute('INSERT OR IGNORE INTO songSubmission VALUES(?, ?)', [song_name + '--||' + artist_name, curr_time])
        self.cursor.execute('INSERT OR IGNORE INTO idStamped VALUES(?, ?)', [post_id, curr_time])
        self.sql.commit()
    
    @classmethod
    def get_artist_timestamp(self, artist_name):
        self.cursor.execute('SELECT postTime, repeatCount FROM artistSubmission WHERE artist == ?', [artist_name])
        
        return self.cursor.fetchone()
    
    @classmethod
    def replace_entry(self, artist_name, song_name, curr_time, post_id):
        self.cursor.execute('UPDATE artistSubmission SET postTime=? WHERE artist == ?', [curr_time, artist_name])
        self.cursor.execute('INSERT OR REPLACE INTO songSubmission VALUES(?, ?)', [song_name + '--||' + artist_name, curr_time])
        self.cursor.execute('INSERT OR IGNORE INTO idStamped VALUES(?, ?)', [post_id, curr_time])
        self.sql.commit()
    
    @classmethod
    def search_song(self, artist_name, song_name):
        self.cursor.execute('SELECT postTime FROM songSubmission WHERE artistSong == ?', [song_name + '--||' + artist_name])
    
        return self.cursor.fetchone()
    
    @classmethod
    def get_submissions_before_time(self, time_threshold):
        self.cursor.execute('SELECT postID FROM idStamped WHERE postTime < ?', [time_threshold])
        idList = self.cursor.fetchall()
        
        self.cursor.execute('DELETE FROM idStamped WHERE postTime < ?', [time_threshold])
        self.sql.commit()
        
        return idList
    
    @classmethod
    def add_count(self, artist_name):
        self.cursor.execute('UPDATE artistSubmission SET repeatCount = repeatCount + 1 WHERE artist == ?', [artist_name])
        self.sql.commit()
    
    @classmethod
    def delete_old_entries(self, time_threshold):        
        self.cursor.execute('DELETE FROM songSubmission WHERE postTime < ?', [time_threshold])
        self.sql.commit()
    
