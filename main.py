import sys
import time
import traceback

import pylast
from praw import Reddit

from blottertrax.helper import templates
from blottertrax.config import Config
from blottertrax.database import Database
from blottertrax.helper.excluded_artists import ExcludedArtists
from blottertrax.services.lastfm import LastFM
from blottertrax.services.youtube import Youtube
from blottertrax.services.soundcloud import Soundcloud
from blottertrax.helper.title_parser import TitleParser


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'BlotterTrax /r/listentothis submission bot by /u/plebianlinux'
    config: Config = None
    last_fm: LastFM = None
    database: Database = None
    crash_timeout: int = 10
    services: list = None

    def __init__(self):
        try:
            self.config = Config()
            self.last_fm = LastFM()
            self.database = Database()
            self.services = [Youtube(), Soundcloud(), self.last_fm]

            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)

        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self._get_submissions():
            exceeds_threshold = False

            try:
                parsed_submission = TitleParser.create_parsed_submission_from_submission(submission)
            except LookupError:
                # Can't find artist from submission name, skipping
                self.database.log_error_causing_submission(None, submission, traceback.format_exc(), True)
                continue

            if ExcludedArtists.is_excluded(parsed_submission.artist) is True:
                continue

            for service in self.services:
                try:
                    result = service.get_service_result(parsed_submission)

                    if result.exceeds_threshold is False:
                        continue

                    self._perform_exceeds_threshold_mod_action(submission, result)
                    exceeds_threshold = True

                except Exception:
                    # Go ahead and continue execution, don't want to fail completely just because one service failed.
                    traceback.print_exc(file=sys.stdout)
                    self.database.log_error_causing_submission(parsed_submission, submission, traceback.format_exc())

                    pass
                finally:
                    self.database.save_submission(submission)

            # Yeey this post probably isn't breaking the rules 🌈
            try:
                if self.config.SEND_ARTIST_REPLY is True and exceeds_threshold is False:
                    self._reply_with_sticky_post(submission, self.last_fm.get_artist_reply(parsed_submission))
            except (pylast.WSError, LookupError):
                # Can't find artist, continue execution
                continue

    def _get_submissions(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            print(submission.title + " - http://reddit.com" + submission.permalink)

            if self.database.known_submission(submission) is True:
                continue

            if submission.is_self is True:
                self.database.save_submission(submission)
                # We currently don't do anything further with self posts.  Move to the next post.
                continue

            yield submission

    def _perform_exceeds_threshold_mod_action(self, submission, service):
        if self.config.REMOVE_SUBMISSIONS is True:
            self._remove_submission_exceeding_threshold(submission, service)
        else:
            submission.report(templates.mod_note_exceeding_threshold.format(service.service_name, service.threshold,
                                                                            service.listeners_count))

    def _remove_submission_exceeding_threshold(self, submission, service):
        reply = templates.submission_exceeding_threshold.format(
            submission.author.name, service.service_name, service.threshold, service.listeners_count, submission.id
        )
        # This is *theoretically* supposed to add a modnote to the removal reason so mods know why.
        # Currently not working?
        mod_message = templates.mod_note_exceeding_threshold.format(service.service_name, service.threshold,
                                                                    service.listeners_count)
        submission.mod.remove(False, mod_message)
        self._reply_with_sticky_post(submission, reply)

    @staticmethod
    def _reply_with_sticky_post(submission, reply_text):
        comment = submission.reply(reply_text)
        comment.mod.distinguish("yes", sticky=True)

    def daemon(self):
        try:
            self._run()
        except Exception:
            traceback.print_exc(file=sys.stdout)
            time.sleep(self.crash_timeout)
            self.daemon()


if __name__ == '__main__':
    BlotterTrax().daemon()
