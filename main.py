import re
import time
from urllib.parse import urlparse

import pylast
from praw import Reddit

from config import Config
from database import Database
from lastfm import LastFM
from youtube import Youtube


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'BlotterTrax /r/listentothis submission bot by /u/plebianlinux'
    config: Config = Config()
    youtube: Youtube = Youtube()
    last_fm: LastFM = LastFM()
    database: Database = Database()
    crash_timeout: int = 10

    def __init__(self):
        try:
            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)
        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            if self.database.known_submission(submission) is True:
                continue

            if submission.is_self is True:
                if '[discussion]' not in str(submission.title).lower():
                    self._archive_text_post_without_discussion_tag(submission)
                else:
                    self.database.save_submission(submission)
                continue

            url = re.search("(?P<url>https?://[^\s]+)", submission.url).group("url")

            parsed_url = urlparse(url)
            youtube_service = self.youtube.get_service_result(parsed_url)

            if youtube_service.exceeds_threshold:
                self._archive_submission_exceeding_threshold(submission, youtube_service.service_name,
                                                             youtube_service.threshold, youtube_service.listeners_count)
                continue

            artist_name = self._extract_artist_post_title(submission.title)

            try:
                last_fm_service = self.last_fm.get_service_result(artist_name)
            except pylast.WSError:
                continue

            if last_fm_service.exceeds_threshold:
                self._archive_submission_exceeding_threshold(submission, last_fm_service.service_name,
                                                             last_fm_service.threshold, last_fm_service.listeners_count)
                continue

            # Yeey this post probably isn't breaking the rules 🌈
            comment = submission.reply(self.last_fm.get_artist_reply(artist_name))
            comment.mod.distinguish("yes", sticky=True)
            self.database.save_submission(submission)

    def _archive_submission_exceeding_threshold(self, submission, service, threshold, count):
        reply = '''
All apologies /u/{} but your post has been automatically removed because the artist has too many {}. The maximum is {:,}, this link has {:,}.
If you think this is in error, please [contact the mods](https://www.reddit.com/message/compose?to=/r/listentothis&subject=Post+removed+in+error.&message=https://redd.it/{}). 

If you're new to the subreddit, please read the full list of removal reasons.

_Don't blame me,_ [_I'm just a bot_](https://www.youtube.com/watch?v=jqaweMZv4Og)|[_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
        '''.format(submission.author.name, service, threshold, count, submission.id)

        comment = submission.reply(reply)
        comment.mod.distinguish("yes", sticky=True)

        submission.mod.remove()
        self.database.save_submission(submission)

    def _archive_text_post_without_discussion_tag(self, submission):
        reply = '''
All apologies /u/{} but your post has been automatically removed because it is a text post without the [Discussion] tag 

If you're new to the subreddit, please read the full list of removal reasons.

_Don't blame me,_ [_I'm just a bot_](https://www.youtube.com/watch?v=jqaweMZv4Og)|[_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
                '''.format(submission.author.name, submission.id)

        comment = submission.reply(reply)
        comment.mod.distinguish("yes", sticky=True)

        submission.mod.remove()

        self.database.save_submission(submission)

    @staticmethod
    def _extract_artist_post_title(post_title):
        return post_title.split(' -')[0]

    def daemon(self):
        try:
            self._run()
        except Exception as exception:
            print(str(exception))
            time.sleep(self.crash_timeout)
            self.daemon()


if __name__ == '__main__':
    BlotterTrax().daemon()
