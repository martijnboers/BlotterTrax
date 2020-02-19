import re

import pylast

import templates
from config import Config
from serviceresult import ServiceResult


class LastFM:
    network = None
    config: Config = Config()
    threshold_scrobbles = 4_000_000
    threshold_listeners = 250_000

    def __init__(self):
        self.network = pylast.LastFMNetwork(api_key=self.config.LASTFM_KEY, api_secret=self.config.LASTFM_SECRET,
                                            username=self.config.LASTFM_USERNAME,
                                            password_hash=pylast.md5(self.config.LASTFM_PASSWORD))

    def get_service_result(self, artist_name: str) -> ServiceResult:
        """
        Gets the last fm statistics for the artist name and verifies if it exceeds the given thresholds
        """
        artist = self.network.get_artist(artist_name)

        listeners = artist.get_listener_count()
        scrobbles = artist.get_playcount()

        if listeners > self.threshold_listeners:
            return ServiceResult(True, listeners, self.threshold_listeners, 'Last.fm listeners')

        if scrobbles > self.threshold_scrobbles:
            return ServiceResult(True, scrobbles, self.threshold_scrobbles, 'Last.fm artist scrobbles')

        return ServiceResult(False, scrobbles, 0, '')

    def get_artist_reply(self, artist_name) -> str:
        """
        Get the formatted artist reply with appended last.fm data
        """
        artist = self.network.get_artist(artist_name)

        listeners = artist.get_listener_count()

        description = str(artist.get_bio_summary())

        # Strip out last.fm link from description
        description = re.sub(r'<a href="https://www\.last\.fm/.*">Read more on Last\.fm</a>', '', description)

        # Fix formatting for linebreaks
        description = description.replace("\n", "\n>")

        if description == '':
            raise LookupError

        plays = artist.get_playcount()
        top_tags = artist.get_top_tags(limit=5)
        last_fm_url = artist.get_url()

        tag_string = ', '.join(map(lambda t: t.item.get_name(), top_tags))

        return templates.reply_with_last_fm_info.format(
            artist_name, description, last_fm_url, listeners, plays, tag_string
        )
