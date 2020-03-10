class ParsedSubmission:
    artist: str
    featuring_artist: str
    track_title: str
    url: str
    success: bool

    def __init__(self, success: bool, artist: str, featuring_artist: str, track_title: str, url: str):
        self.success = success
        self.artist = artist
        self.featuring_artist = featuring_artist
        self.track_title = track_title
        self.url = url
