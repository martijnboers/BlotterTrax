import sys
import time
import traceback

from praw import Reddit

from blottertrax.config import Config
from blottertrax.database import Database
from blottertrax.description_provider import DescriptionProvider
from blottertrax.exceptions.description_exception import DescriptionException
from blottertrax.helper import templates
from blottertrax.helper.excluded_artists import ExcludedArtists
from blottertrax.helper.self_promo_detector import SelfPromoDetector
from blottertrax.helper.title_parser import TitleParser
from blottertrax.services.lastfm import LastFM
from blottertrax.services.soundcloud import Soundcloud
from blottertrax.services.youtube import Youtube


class BlotterTrax:
    useragent: str = 'BlotterTrax /r/listentothis submission bot'
    reddit: Reddit = None
    config: Config = None
    last_fm: LastFM = None
    database: Database = None
    description_provider: DescriptionProvider = None
    crash_timeout: int = 10
    threshold_services: list = None

    def __init__(self):
        try:
            self.config = Config()
            self.last_fm = LastFM()
            self.database = Database()
            self.description_provider = DescriptionProvider()
            self.threshold_services = [Youtube(), Soundcloud(), self.last_fm]

            self.reddit = Reddit(client_id=self.config.CLIENT_ID, client_secret=self.config.CLIENT_SECRET,
                                 password=self.config.PASSWORD, user_agent=self.useragent,
                                 username=self.config.USER_NAME)

        except KeyError:
            exit('Check if the configuration is set right')

    def _run(self):
        for submission in self._get_submissions():
            parsed_submission = TitleParser.create_parsed_submission_from_submission(submission)

            if ExcludedArtists.is_excluded(parsed_submission):
                continue

            if SelfPromoDetector.is_self_promo(parsed_submission, submission):
                reply = templates.self_promotion.format(submission.author.name)
                submission.mod.remove(False, mod_note="Self promotion")
                self._reply_with_sticky_post(submission, reply)
                continue

            exceeds_threshold = self._do_service_checks(parsed_submission, submission)

            try:
                if exceeds_threshold is False and parsed_submission.success is True:
                    # Yeey this post probably isn't breaking the rules 🌈
                    self._reply_with_sticky_post(submission, self.description_provider.get_reply(parsed_submission))
            except DescriptionException:
                # Can't find recording on Musicbrainz, skipping
                # traceback.print_exc(file=sys.stdout)
                pass

    def _do_service_checks(self, parsed_submission, submission) -> bool:
        """
        Loop through all services and check them to determine if we need to remove the post for exceeding thresholds.
        """
        exceeds_threshold = False

        for service in self.threshold_services:
            try:
                # Some services can run without a successful parsed submission and just need the url
                # If this is not the case, lets skip it now.
                if service.requires_fully_parsed_submission() and not parsed_submission.success:
                    continue

                result = service.get_service_result(parsed_submission)

                if result.exceeds_threshold is True:
                    self._perform_exceeds_threshold_mod_action(submission, result)
                    exceeds_threshold = True
                    break

            except Exception:
                # Go ahead and continue execution, don't want to fail completely just because one service failed.
                traceback.print_exc(file=sys.stdout)
                self.database.log_error_causing_submission(parsed_submission, submission, traceback.format_exc())

        return exceeds_threshold

    def _get_submissions(self):
        for submission in self.reddit.subreddit(self.config.SUBREDDIT).stream.submissions():
            print(submission.title + " - http://reddit.com" + submission.permalink)

            if self.database.known_submission(submission) is True:
                continue

            # Always save submissions, in case of errors log it and continue
            self.database.save_submission(submission)

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
        submission.mod.remove(False, mod_note=mod_message)
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
