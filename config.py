import configparser
import os


class Config:
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    PASSWORD = ''
    USER_NAME = ''
    YT_KEY = ''

    def __init__(self):
        config = configparser.ConfigParser()

        try:
            config.read('{}/conf/reddit-credentials.ini'.format(os.path.dirname(os.path.realpath(__file__))))
            self.CLIENT_ID = config['REDDIT']['CLIENT_ID']
            self.CLIENT_SECRET = config['REDDIT']['CLIENT_SECRET']
            self.PASSWORD = config['REDDIT']['PASSWORD']
            self.USER_NAME = config['REDDIT']['USER_NAME']

            self.YT_KEY = config['YOUTUBE']['KEY']

        except Exception:
            exit("Please make sure reddit-credentials.ini is set")