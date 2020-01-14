import configparser
import os


class Config:
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    PASSWORD = ''
    USER_NAME = ''

    def __init__(self):
        config = configparser.ConfigParser()

        try:
            print('SECRET' + self.CLIENT_SECRET)
            config.read('{}/conf/reddit-credentials.ini'.format(os.path.dirname(os.path.realpath(__file__))))
            self.CLIENT_ID = config['REDDIT']['CLIENT_ID']
            self.CLIENT_SECRET = config['REDDIT']['CLIENT_SECRET']
            self.PASSWORD = config['REDDIT']['PASSWORD']
            self.USER_NAME = config['REDDIT']['USER_NAME']

        except Exception:
            exit("Please make sure reddit-credentials.ini is set")