import re
import time
from urllib import parse
from urllib.parse import urlparse

from praw import Reddit

from config import Config
from youtube import Youtube


class BlotterTrax:
    reddit: Reddit = None
    useragent = 'Tbd'
    config = Config()
    youtube = Youtube()
    youtubeUrls = ['youtube.com', 'youtube.be', 'www.youtube.com']

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
            url = re.search("(?P<url>https?://[^\s]+)", submission.url).group("url")

            if url is None:
                continue

            parsedUrl = urlparse(url)

            if parsedUrl.netloc not in self.youtubeUrls:
                continue

            query = parse.parse_qs(parse.urlsplit(url).query)

            viewCount = self.youtube.video(query['v'][0])

            if viewCount > 50000:
                print('TODO: archive reddit post ')

    def deamon(self):
        while True:
            self._run()
            time.sleep(0.5)


if __name__ == '__main__':
    BlotterTrax().deamon()
