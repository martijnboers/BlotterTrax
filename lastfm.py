import re

import pylast

from config import Config


class LastFM:
    network = None
    config: Config = Config()
    threshold_scrobbles = 4_000_000
    threshold_listeners = 250_000

    def __init__(self):

        self.network = pylast.LastFMNetwork(api_key=self.config.LASTFM_KEY, api_secret=self.config.LASTFM_SECRET,
                                            username=self.config.LASTFM_USERNAME,
                                            password_hash=pylast.md5(self.config.LASTFM_PASSWORD))

    def exceeds_threshold(self, artist_name):
        artist = self.network.get_artist(artist_name)
        listeners = None
        scrobbles = None

        try:
            listeners = artist.get_listener_count()
            scrobbles = artist.get_playcount()
        except pylast.WSError:
            # Can't find artist
            return {'exceeds': False}

        if listeners > self.threshold_listeners:
            return {'exceeds': True, 'count': listeners,
                    'threshold': self.threshold_listeners, 'service': 'Last.fm listeners'}

        if scrobbles > self.threshold_scrobbles:
            return {'exceeds': True, 'count': scrobbles,
                    'threshold': self.threshold_scrobbles, 'service': 'Last.fm artist scrobles'}

        return {'exceeds': False}

    def get_artist_reply(self, artist_name):
        artist = self.network.get_artist(artist_name)
        listeners = None

        try:
            listeners = artist.get_listener_count()
        except pylast.WSError:
            return self._cant_find_artist_reply()

        description = str(artist.get_bio_summary())

        # Strip out last.fm link from description
        description = re.sub(r'<a href="https://www\.last\.fm/.*">Read more on Last\.fm</a>', '', description)

        # Fix formatting for linebreaks
        description = description.replace("\n", "\n>")

        if description == '':
            return self._cant_find_artist_reply()

        plays = artist.get_playcount()
        top_tags = artist.get_top_tags(limit=5)
        last_fm_url = artist.get_url()

        tag_string = ', '.join(map(lambda t: t.item.get_name(), top_tags))

        comment = '''
**{}**

> {}

[last.fm]({}): {:,} listeners, {:,} plays

tags: {}
        '''.format(artist_name, description, last_fm_url, listeners, plays, tag_string)

        return comment

    @staticmethod
    def _cant_find_artist_reply():
        return '''
Can't find the artist on last.fm or artists doesn't have a description.

Make sure you spelled it right or if you can; add this artist to last.fm

_Don't blame me,_ [_I'm just a bot_](https://www.youtube.com/watch?v=jqaweMZv4Og)|[_Bugs & Code_](https://github.com/martijnboers/BlotterTrax)
            '''
