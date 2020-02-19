import re
import sys
import time
import traceback
from urllib.parse import urlparse

import pylast
from praw import Reddit

from config import Config
from database import Database
from lastfm import LastFM
import templates
from youtube import Youtube


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'BlotterTrax /r/listentothis submission bot by /u/plebianlinux'
    config: Config = None
    youtube: Youtube = None
    last_fm: LastFM = None
    database: Database = None
    crash_timeout: int = 10

    def __init__(self):
        try:
            self.config = Config()
            self.youtube = Youtube()
            self.last_fm = LastFM()
            self.database = Database()

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
                self.database.save_submission(submission)

            url = re.search("(?P<url>https?://[^\s]+)", submission.url).group("url")

            parsed_url = urlparse(url)

            artist_name = self._get_artist_name_from_submission_title(submission.title)

            youtube_service = self.youtube.get_service_result(parsed_url)

            if youtube_service.exceeds_threshold is True:
                self._perform_exceeds_threshold_mod_action(submission, youtube_service)
                self.database.save_submission(submission)
                continue

            try:
                last_fm_service = self.last_fm.get_service_result(artist_name)
                if last_fm_service.exceeds_threshold is True:
                    self._perform_exceeds_threshold_mod_action(submission, last_fm_service)
                    self.database.save_submission(submission)
                    continue
            except pylast.WSError:
                # Go ahead and continue execution.  Don't want to fail completely just because one service failed.
                pass

            # Yeey this post probably isn't breaking the rules 🌈
            try:
                self._reply_with_sticky_post(submission, self.last_fm.get_artist_reply(artist_name))
                # Made it all the way.  Save submission record.
                self.database.save_submission(submission)
            except (pylast.WSError, LookupError):
                # Can't find artist, continue execution
                continue

    def _perform_exceeds_threshold_mod_action(self, submission, service):
        if self.config.REMOVE_SUBMISSIONS is True:
            self._remove_submission_exceeding_threshold(submission, service)
        else:
            submission.report('''BlotterTrax: {} exceeds {:,}.  Actual: {:,}'''.format(service.service_name, service.threshold, service.listeners_count))

    def _remove_submission_exceeding_threshold(self, submission, service):
        reply = templates.submission_exceeding_threshold.format(
            submission.author.name, service.service_name, service.threshold, service.count, submission.id
        )
        submission.mod.remove()
        self._reply_with_sticky_post(submission, reply)

    def _reply_with_sticky_post(self, submission, reply_text):
        comment = submission.reply(reply_text)
        comment.mod.distinguish("yes", sticky=True)

    @staticmethod
    def _get_artist_name_from_submission_title(post_title):
        artist = re.search(r'(?P<artist>.+?) \s*(-|—)\s*', post_title, re.IGNORECASE)
        feature_artist = re.search(
            r'(?P<artist>.+?)\s*(&|feat.?|ft\.?|feature|featuring)\s*(?P<featureArtist>.+?)\s*(-|—)\s*',
            post_title, re.IGNORECASE
        )

        if feature_artist is not None:
            # If there is a featuring artists, it should use the feature_artist artist result
            return feature_artist.group('artist')
        if artist.group('artist') is not None:
            return artist.group('artist')

        raise LookupError

    def daemon(self):
        try:
            self._run()
        except Exception:
            traceback.print_exc(file=sys.stdout)
            time.sleep(self.crash_timeout)
            self.daemon()


if __name__ == '__main__':
    BlotterTrax().daemon()
