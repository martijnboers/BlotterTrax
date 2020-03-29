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
    SOUNDCLOUD_KEY: str = ''
    MUSICBRAINZ_USER: str = ''
    MUSICBRAINZ_PASSWORD: str = ''

    def __init__(self):
        config = configparser.ConfigParser(strict=False, interpolation=None)

        try:
            config.read('{}/../conf/config.ini'.format(os.path.dirname(os.path.realpath(__file__))))
            self.CLIENT_ID = config.get('REDDIT', 'CLIENT_ID')
            self.CLIENT_SECRET = config.get('REDDIT', 'CLIENT_SECRET')
            self.PASSWORD = config.get('REDDIT', 'PASSWORD')
            self.USER_NAME = config.get('REDDIT', 'USER_NAME')
            self.SUBREDDIT = config.get('REDDIT', 'SUBREDDIT')
            self.REMOVE_SUBMISSIONS = config.getboolean('REDDIT', 'REMOVE_SUBMISSIONS')

            self.YT_KEY = config.get('YOUTUBE', 'KEY')

            self.LASTFM_KEY = config.get('LASTFM', 'KEY')
            self.LASTFM_SECRET = config.get('LASTFM', 'SECRET')
            self.LASTFM_USERNAME = config.get('LASTFM', 'USERNAME')
            self.LASTFM_PASSWORD = config.get('LASTFM', 'PASSWORD')

            self.SOUNDCLOUD_KEY = config.get('SOUNDCLOUD', 'KEY')

            self.MUSICBRAINZ_USER = config.get('MUSICBRAINZ', 'USER')
            self.MUSICBRAINZ_PASSWORD = config.get('MUSICBRAINZ', 'PASSWORD')

        except Exception:
            exit("Please make sure conf/config.ini is set")
