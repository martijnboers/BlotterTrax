class ParsedSubmission:
    artist: str
    featuring_artist: str
    track_title: str

    def __init__(self, artist: str, featuring_artist: str, track_title: str):
        self.artist = artist
        self.featuring_artist = featuring_artist
        self.track_title = track_title
