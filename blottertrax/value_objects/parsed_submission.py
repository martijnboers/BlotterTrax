class ParsedSubmission:
    artist: str
    featuring_artist: str
    song_title: str
    url: str
    id: str

    def __init__(self, artist: str, featuring_artist: str, song_title: str, url, id: str):
        self.artist = artist
        self.featuring_artist = featuring_artist
        self.song_title = song_title
        self.url = url
        self.id = id
