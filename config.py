import configparser
import os


class Config:
    CLIENT_ID: str = ''
    CLIENT_SECRET: str = ''
    PASSWORD: str = ''
    USER_NAME: str = ''
    YT_KEY: str = ''
    SUBREDDIT: str = ''

    def __init__(self):
        config = configparser.ConfigParser()

        try:
            config.read('{}/conf/reddit-credentials.ini'.format(os.path.dirname(os.path.realpath(__file__))))
            self.CLIENT_ID = config['REDDIT']['CLIENT_ID']
            self.CLIENT_SECRET = config['REDDIT']['CLIENT_SECRET']
            self.PASSWORD = config['REDDIT']['PASSWORD']
            self.USER_NAME = config['REDDIT']['USER_NAME']
            self.SUBREDDIT = config['REDDIT']['SUBREDDIT']

            self.YT_KEY = config['YOUTUBE']['KEY']

        except Exception:
            exit("Please make sure reddit-credentials.ini is set")