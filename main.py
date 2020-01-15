import re
from urllib import parse
from urllib.parse import urlparse

from praw import Reddit

from config import Config
from youtube import Youtube


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'Tbd'
    config: Config = Config()
    youtube: Youtube = Youtube()

    def __init__(self):
        try:
            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)
        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            url = re.search("(?P<url>https?://[^\s]+)", submission.url).group("url")

            if url is None:
                continue

            parsedUrl = urlparse(url)
            youtubeLimit = self.youtube.exceedsThreshold(parsedUrl)

            if youtubeLimit['exceeds']:
                self._archieve(submission, youtubeLimit['threshold'], youtubeLimit['count'])
                continue

    def _archieve(self, submission, threshold, count):
        reply = '''
All apologies /u/{} but your post has been automatically removed because the artist has too many youtube plays. The maximum is {}, this link has {}.
If you think this is in error, please [contact the mods](https://www.reddit.com/message/compose?to=/r/listentothis&subject=Post+removed+in+error.&message=https://redd.it/cdlzgi). 

If you're new to the subreddit, please read the full list of removal reasons.

_Don't blame me,_ [_I'm just a bot_](https://www.youtube.com/watch?v=jqaweMZv4Og)|[_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
        '''.format(submission.author.name, threshold, count)

        comment = submission.reply(reply)
        comment.mod.distinguish("yes", sticky=True)

        submission.mod.remove()

        # TODO: start saving processed submissions

    def deamon(self):
        self._run()


if __name__ == '__main__':
    BlotterTrax().deamon()
