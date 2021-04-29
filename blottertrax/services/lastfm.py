import pylast

from blottertrax.config import Config
from blottertrax.exceptions.service_requires_parsed_submission import ServiceRequiresParsedSubmission
from blottertrax.services.threshold_service import ThresholdService
from blottertrax.value_objects.parsed_submission import ParsedSubmission
from blottertrax.value_objects.service_result import ThresholdServiceResult


class LastFM(ThresholdService):
    config: Config = Config()
    threshold_scrobbles = config.LASTFM.SCROBBLE_THRESHOLD
    threshold_listeners = config.LASTFM.LISTENER_THRESHOLD

    def __init__(self):
        self.network = pylast.LastFMNetwork(api_key=self.config.LASTFM.KEY, api_secret=self.config.LASTFM.SECRET,
                                            username=self.config.LASTFM.USERNAME,
                                            password_hash=pylast.md5(self.config.LASTFM.PASSWORD))

    def get_service_result(self, parsed_submission: ParsedSubmission) -> ThresholdServiceResult:
        """
        Gets the last fm statistics for the artist name and verifies if it exceeds the given thresholds
        """
        if parsed_submission.success is False:
            raise ServiceRequiresParsedSubmission()

        artist = self.network.get_artist(parsed_submission.artist)

        listeners = artist.get_listener_count()
        scrobbles = artist.get_playcount()

        if listeners > self.threshold_listeners:
            return ThresholdServiceResult(True, listeners, self.threshold_listeners, 'Last.fm listeners')

        if scrobbles > self.threshold_scrobbles:
            return ThresholdServiceResult(True, scrobbles, self.threshold_scrobbles, 'Last.fm artist scrobbles')

        return ThresholdServiceResult(False, scrobbles, 0, '')

    def requires_fully_parsed_submission(self):
        return True
