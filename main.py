import sys
import time
import traceback

import pylast
from praw import Reddit

import templates
from config import Config
from database import Database
from lastfm import LastFM
from youtube import Youtube
from soundcloud import Soundcloud
from title_parser import TitleParser


class BlotterTrax:
    reddit: Reddit = None
    useragent: str = 'BlotterTrax /r/listentothis submission bot by /u/plebianlinux'
    config: Config = None
    youtube: Youtube = None
    soundcloud: Soundcloud = None
    last_fm: LastFM = None
    database: Database = None
    crash_timeout: int = 10

    def __init__(self):
        try:
            self.config = Config()
            self.youtube = Youtube()
            self.soundcloud = Soundcloud()
            self.last_fm = LastFM()
            self.database = Database()

            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)

        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            print(submission.permalink)  # Print this to console just so we know we got a new submission.
            if self.database.known_submission(submission) is True:
                continue

            if submission.is_self is True:
                self.database.save_submission(submission)
                # We currently don't do anything further with self posts.  Move to the next post.
                continue

            try:
                artist_name = TitleParser.get_artist_name_from_submission_title(submission.title)
            except LookupError:
                # Can't find artist from submission name, skipping
                self.database.save_submission(submission)
                continue

            # Get artist for most future use
            prio_artist = TitleParser.get_prioritized_artist(artist_name)

            try:
                # Check Youtube.
                youtube_service = self.youtube.get_service_result(submission.url)
                if youtube_service.exceeds_threshold is True:
                    self._perform_exceeds_threshold_mod_action(submission, youtube_service)
                    self.database.save_submission(submission)
                    continue
            except Exception as e:
                print("The following unhandled exception occurred during YouTube lookup:")
                print(e)

            try:
                # Check Soundcloud.
                soundcloud_service = self.soundcloud.get_service_result(submission.url)
                if soundcloud_service.exceeds_threshold is True:
                    self._perform_exceeds_threshold_mod_action(submission, soundcloud_service)
                    self.database.save_submission(submission)
                    continue
            except Exception as e:
                print("The following unhandled exception occurred during Soundcloud lookup:")
                print(e)

            try:
                # Check Last.FM
                last_fm_service = self.last_fm.get_service_result(prio_artist)
                if last_fm_service.exceeds_threshold is True:
                    self._perform_exceeds_threshold_mod_action(submission, last_fm_service)
                    self.database.save_submission(submission)
                    continue
            except pylast.WSError:
                # Go ahead and continue execution.  Don't want to fail completely just because one service failed.
                pass
            except Exception as e:
                print("The following unhandled exception occurred during LastFM lookup:")
                print(e)

            # Yeey this post probably isn't breaking the rules 🌈
            try:
                if self.config.SEND_ARTIST_REPLY is True:
                    self._reply_with_sticky_post(submission, self.last_fm.get_artist_reply(prio_artist))
                # Made it all the way.  Save submission record.
                self.database.save_submission(submission)
            except (pylast.WSError, LookupError):
                # Can't find artist, continue execution
                continue

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

        self._reply_with_sticky_post(submission, reply)
        mod_message = templates.mod_note_exceeding_threshold.format(service.service_name, service.threshold,
                                                                    service.listeners_count)
        # This is *theoretically* supposed to add a modnote to the removal reason so mods know why.  Currently not working?
        submission.mod.remove(False, mod_message)

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
