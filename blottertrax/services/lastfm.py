import re

import pylast

from blottertrax.exceptions.empty_description import EmptyDescription
from blottertrax.exceptions.service_requires_parsed_submission import ServiceRequiresParsedSubmission
from blottertrax.helper import templates
from blottertrax.config import Config
from blottertrax.value_objects.parsed_submission import ParsedSubmission
from blottertrax.value_objects.service_result import ServiceResult


class LastFM:
    network = None
    config: Config = Config()
    threshold_scrobbles = 4_000_000
    threshold_listeners = 250_000

    def __init__(self):
        self.network = pylast.LastFMNetwork(api_key=self.config.LASTFM_KEY, api_secret=self.config.LASTFM_SECRET,
                                            username=self.config.LASTFM_USERNAME,
                                            password_hash=pylast.md5(self.config.LASTFM_PASSWORD))

    def get_service_result(self, parsed_submission: ParsedSubmission) -> ServiceResult:
        """
        Gets the last fm statistics for the artist name and verifies if it exceeds the given thresholds
        """
        if parsed_submission.success is False:
            raise ServiceRequiresParsedSubmission()

        artist = self.network.get_artist(parsed_submission.artist)

        listeners = artist.get_listener_count()
        scrobbles = artist.get_playcount()

        if listeners > self.threshold_listeners:
            return ServiceResult(True, listeners, self.threshold_listeners, 'Last.fm listeners')

        if scrobbles > self.threshold_scrobbles:
            return ServiceResult(True, scrobbles, self.threshold_scrobbles, 'Last.fm artist scrobbles')

        return ServiceResult(False, scrobbles, 0, '')

    def get_artist_reply(self, parsed_submission: ParsedSubmission) -> str:
        """
        Get the formatted artist reply with appended last.fm data
        """
        artist = self.network.get_artist(parsed_submission.artist)

        listeners = artist.get_listener_count()

        description = str(artist.get_bio_summary())

        # Strip out last.fm link from description
        description = re.sub(r'<a href="https://www\.last\.fm/.*">Read more on Last\.fm</a>', '', description)

        # Fix formatting for linebreaks
        description = description.replace("\n", "\n>")

        if description == '':
            raise EmptyDescription

        plays = artist.get_playcount()
        top_tags = artist.get_top_tags(limit=5)
        last_fm_url = artist.get_url()

        tag_string = ', '.join(map(lambda t: t.item.get_name(), top_tags))

        return templates.reply_with_last_fm_info.format(
            parsed_submission.artist, description, last_fm_url, listeners, plays, tag_string
        )
