import requests


class ParsedSubmission:
    artist: str
    featuring_artist: str
    track_title: str
    url: str
    success: bool
    final_url: str = ''

    def __init__(self, success: bool, url: str, artist: str = '', featuring_artist: str = '', track_title: str = ''):
        self.success = success
        self.artist = artist
        self.featuring_artist = featuring_artist
        self.track_title = track_title
        self.url = url

    def get_final_url(self):
        # we already did the work once, just return the result
        if self.final_url != '':
            return self.final_url

        # Follow URL to the end location in case of URL shorteners
        session = requests.Session()  # so connections are recycled
        resp = session.head(self.url, allow_redirects=True)
        self.final_url = resp.url
        return self.final_url
