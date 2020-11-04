import configparser
import os


class _ConfigBase:
    # We don't want to accidentally add anything to this config.
    # This allows us to throw and error in the __new__ call above if a programmer makes a typo.
    # For instance, using cls._instance.YOUTUBE_CLIENT_SECRET rather than cls._instance.YOUTUBE.CLIENT_SECRET
    def __setattr__(self, key, value):
        if hasattr(self, key):
            object.__setattr__(self, key, value)
        else:
            raise TypeError(
                "{} is a frozen class.  You cannot dynamically add properties.  Property attempted: {}, value: {}".format(
                    self, key, value))


class Config(_ConfigBase):
    _instance = None

    # Note: You must specify a default value.  The value of None is fine.
    class _REDDIT(_ConfigBase):
        CLIENT_ID: str = None
        CLIENT_SECRET: str = None
        USER_NAME: str = None
        PASSWORD: str = None

        SUBREDDIT: str = None
        REMOVE_SUBMISSIONS_ON_ERROR: bool = False
        MINIMUM_ACCOUNT_AGE = 200
        MINIMUM_COMMENT_KARMA = 50
        USER_AGENT = "BlotterTrax /r/listentothis submission bot"

    class _YOUTUBE(_ConfigBase):
        KEY: str = None
        THRESHOLD: int = 1_000_000

    class _LASTFM(_ConfigBase):
        KEY: str = None
        SECRET: str = None
        USERNAME: str = None
        PASSWORD: str = None
        LISTENER_THRESHOLD: int = 500_000
        SCROBBLE_THRESHOLD: int = 4_000_000

    class _SOUNDCLOUD(_ConfigBase):
        KEY: str = None
        THRESHOLD: int = 1_000_000

    class _MUSICBRAINZ(_ConfigBase):
        USER: str = None
        PASSWORD: str = None

    class _APP(_ConfigBase):
        OVERALL_LISTEN_THRESHOLD: int = 2_000_000

    REDDIT: _REDDIT = _REDDIT()
    YOUTUBE: _YOUTUBE = _YOUTUBE()
    LASTFM: _LASTFM = _LASTFM()
    SOUNDCLOUD: _SOUNDCLOUD = _SOUNDCLOUD()
    MUSICBRAINZ: _MUSICBRAINZ = _MUSICBRAINZ()
    APP: _APP = _APP()

    # Ensure singleton so we aren't reading the config over and over for each service using it.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            config = configparser.ConfigParser(strict=False, interpolation=None)

            try:
                config.read('{}/../conf/config.ini'.format(os.path.dirname(os.path.realpath(__file__))))
                cls._instance.REDDIT.CLIENT_ID = config.get('REDDIT', 'CLIENT_ID')
                cls._instance.REDDIT.CLIENT_SECRET = config.get('REDDIT', 'CLIENT_SECRET')
                cls._instance.REDDIT.PASSWORD = config.get('REDDIT', 'PASSWORD')
                cls._instance.REDDIT.USER_NAME = config.get('REDDIT', 'USER_NAME')
                cls._instance.REDDIT.SUBREDDIT = config.get('REDDIT', 'SUBREDDIT')

                cls._instance.REDDIT.MINIMUM_ACCOUNT_AGE = config.getint('REDDIT', 'MINIMUM_ACCOUNT_AGE')
                cls._instance.REDDIT.MINIMUM_COMMENT_KARMA = config.getint('REDDIT', 'MINIMUM_COMMENT_KARMA')
                cls._instance.REDDIT.USER_AGENT = config.get('REDDIT', 'USER_AGENT')

                cls._instance.REDDIT.REMOVE_SUBMISSIONS_ON_ERROR = config.getboolean('REDDIT', 'REMOVE_SUBMISSIONS')

                cls._instance.YOUTUBE.KEY = config.get('YOUTUBE', 'KEY')

                cls._instance.LASTFM.KEY = config.get('LASTFM', 'KEY')
                cls._instance.LASTFM.SECRET = config.get('LASTFM', 'SECRET')
                cls._instance.LASTFM.USERNAME = config.get('LASTFM', 'USERNAME')
                cls._instance.LASTFM.PASSWORD = config.get('LASTFM', 'PASSWORD')

                cls._instance.LASTFM.LISTENER_THRESHOLD = config.getint('LASTFM', 'LISTENER_THRESHOLD',
                                                                        fallback=500_000)
                cls._instance.LASTFM.SCROBBLE_THRESHOLD = config.getint('LASTFM', 'SCROBBLE_THRESHOLD',
                                                                        fallback=4_000_000)

                cls._instance.SOUNDCLOUD.KEY = config.get('SOUNDCLOUD', 'KEY')
                cls._instance.SOUNDCLOUD.THRESHOLD = config.getint('SOUNDCLOUD', 'THRESHOLD', fallback=1_000_000)

                cls._instance.MUSICBRAINZ.USER = config.get('MUSICBRAINZ', 'USER')
                cls._instance.MUSICBRAINZ.PASSWORD = config.get('MUSICBRAINZ', 'PASSWORD')

                cls._instance.APP.OVERALL_LISTEN_THRESHOLD = config.getint('APP',
                                                                           'OVERALL_LISTEN_THRESHOLD',
                                                                           fallback=3_000_000)

            except TypeError as e:
                print(e)
                exit('Additional field detected on config class.  Please add this in the proper way.')
            except Exception:
                exit("Please make sure conf/config.ini is set")

        return cls._instance

    def is_config_valid(self) -> bool:
        return True
