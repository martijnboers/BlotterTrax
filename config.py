import configparser
import os


class Config:
    CLIENT_ID: str = ''
    CLIENT_SECRET: str = ''
    PASSWORD: str = ''
    USER_NAME: str = ''
    YT_KEY: str = ''
    LASTFM_KEY: str = ''
    LASTFM_SECRET: str = ''
    LASTFM_USERNAME: str = ''
    LASTFM_PASSWORD: str = ''
    SUBREDDIT: str = ''
    REMOVE_SUBMISSIONS: bool = False
    SEND_ARTIST_REPLY: bool = False
    SOUNDCLOUD_KEY: str = ''

    def __init__(self):
        config = configparser.ConfigParser()

        try:
            config.read('{}/conf/config.ini'.format(os.path.dirname(os.path.realpath(__file__))))
            self.CLIENT_ID = config['REDDIT']['CLIENT_ID']
            self.CLIENT_SECRET = config['REDDIT']['CLIENT_SECRET']
            self.PASSWORD = config['REDDIT']['PASSWORD']
            self.USER_NAME = config['REDDIT']['USER_NAME']
            self.SUBREDDIT = config['REDDIT']['SUBREDDIT']
            self.REMOVE_SUBMISSIONS = config.getboolean('REDDIT', 'REMOVE_SUBMISSIONS')
            self.SEND_ARTIST_REPLY = config.getboolean('REDDIT', 'SEND_ARTIST_REPLY')

            self.YT_KEY = config['YOUTUBE']['KEY']

            self.LASTFM_KEY = config['LASTFM']['KEY']
            self.LASTFM_SECRET = config['LASTFM']['SECRET']
            self.LASTFM_USERNAME = config['LASTFM']['USERNAME']
            self.LASTFM_PASSWORD = config['LASTFM']['PASSWORD']
            
            self.SOUNDCLOUD_KEY = config['SOUNDCLOUD']['KEY']

        except Exception:
            exit("Please make sure conf/config.ini is set")
