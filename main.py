import re
import time
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
                if '[discussion]' not in str(submission.title).lower():
                    self._archive_text_post_without_discussion_tag(submission)
                else:
                    self.database.save_submission(submission)
                continue

            url = re.search("(?P<url>https?://[^\s]+)", submission.url).group("url")

            parsed_url = urlparse(url)
            youtube_service = self.youtube.get_service_result(parsed_url)

            if youtube_service.exceeds_threshold is True:
                self._archive_submission_exceeding_threshold(submission, youtube_service.service_name,
                                                             youtube_service.threshold, youtube_service.listeners_count)
                continue

            try:
                artist_name = self._get_artist_name_from_submission_title(submission.title)
            except LookupError:
                self._reply_with_sticky_post(submission, templates.cant_find_artist)

                continue

            try:
                last_fm_service = self.last_fm.get_service_result(artist_name)
            except pylast.WSError:
                continue

            if last_fm_service.exceeds_threshold is True:
                self._archive_submission_exceeding_threshold(submission, last_fm_service.service_name,
                                                             last_fm_service.threshold, last_fm_service.listeners_count)
                continue

            # Yeey this post probably isn't breaking the rules 🌈
            self._reply_with_sticky_post(submission, self.last_fm.get_artist_reply(artist_name))

    def _archive_submission_exceeding_threshold(self, submission, service, threshold, count):
        reply = templates.submission_exceeding_threshold.format(
            submission.author.name, service, threshold, count, submission.id
        )

        self._reply_with_sticky_post(submission, reply, True)

    def _archive_text_post_without_discussion_tag(self, submission):
        reply = templates.submission_missing_discussion_tag.format(submission.author.name, submission.id)

        self._reply_with_sticky_post(submission, reply, True)

    def _reply_with_sticky_post(self, submission, reply_text, remove=False):
        comment = submission.reply(reply_text)
        comment.mod.distinguish("yes", sticky=True)

        if remove is True:
            submission.mod.remove()

        self.database.save_submission(submission)

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
        except Exception as exception:
            print(str(exception))
            time.sleep(self.crash_timeout)
            self.daemon()


if __name__ == '__main__':
    BlotterTrax().daemon()
