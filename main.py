import time

from praw import Reddit
from config import Config


class BlotterTrax:
    reddit: Reddit = None
    useragent = 'Tbd'
    config = Config()

    def __init__(self):
        try:
            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)
        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        subreddit = self.reddit.subreddit('listentothis')

        for submission in subreddit.stream.submissions():
            print(submission)

    def deamon(self):
        while True:
            self._run()
            time.sleep(0.5)


if __name__ == '__main__':
    BlotterTrax().deamon()
