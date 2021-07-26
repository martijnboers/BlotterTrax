import traceback
from multiprocessing import Lock

from praw import Reddit

from blottertrax.config import Config
from blottertrax.database import Database
from blottertrax.description_provider import DescriptionProvider
from blottertrax.exceptions.description_exception import DescriptionException
from blottertrax.helper import templates
from blottertrax.helper.excluded_artists import ExcludedArtists
from blottertrax.helper.self_promo_detector import SelfPromoDetector
from blottertrax.helper.title_parser import TitleParser
from blottertrax.logger import Logger
from blottertrax.services.lastfm import LastFM
from blottertrax.services.overall_threshold_service import OverallThresholdService
from blottertrax.services.soundcloud import Soundcloud
from blottertrax.services.youtube import Youtube


class Submissions:
    threshold_services: list = []

    def __init__(self, lock: Lock):
        try:
            self.config = Config()
            self.logger = Logger()
            self.database = Database(lock)
            self.description_provider = DescriptionProvider()
            self.threshold_services = [Youtube(), Soundcloud(), LastFM()]

            self.reddit = Reddit(client_id=self.config.REDDIT.CLIENT_ID, client_secret=self.config.REDDIT.CLIENT_SECRET,
                                 password=self.config.REDDIT.PASSWORD, user_agent=self.config.REDDIT.USER_AGENT,
                                 username=self.config.REDDIT.USER_NAME)

        except KeyError:
            self.logger.exception('Check if the configuration is set right')
            exit()

    def run(self):
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
                self.logger.error(f"Can't find musicbrainz info for {submission.permalink}")
                pass

    def _do_service_checks(self, parsed_submission, submission) -> bool:
        """
        Loop through all services and check them to determine if we need to remove the post for exceeding thresholds.
        """
        exceeds_threshold = False
        overall_threshold_service = OverallThresholdService()

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
                else:
                    overall_threshold_service.add_service_result(result)

            except Exception:
                # Go ahead and continue execution, don't want to fail completely just because one service failed.
                self.logger.exception(f"Getting {type(service).__name__} failed")
                self.database.log_error_causing_submission(parsed_submission, submission, traceback.format_exc())

        # TODO: Enable this when new rules roll out.
        # # If none of the other checkers exceeded the threshold, check all the combined listeners.
        # if not exceeds_threshold:
        #     result = overall_threshold_service.get_service_result()
        #     if result.exceeds_threshold:
        #         self._perform_exceeds_threshold_mod_action(submission, result)

        return exceeds_threshold

    def _get_submissions(self):
        for submission in self.reddit.subreddit(self.config.REDDIT.SUBREDDIT).stream.submissions():
            if submission is None:
                return None

            if self.database.known_submission(submission) is True:
                continue

            self.logger.info(f"Handling {submission.title} - http://reddit.com{submission.permalink}")

            # Always save submissions, in case of errors log it and continue
            self.database.save_submission(submission)

            yield submission

    def _perform_exceeds_threshold_mod_action(self, submission, service):
        if self.config.REDDIT.REMOVE_SUBMISSIONS_ON_ERROR is True:
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
