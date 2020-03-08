class ExcludedArtists:
    excluded_artists: list = [
        'various artists',
        'anonymous'
    ]

    @staticmethod
    def is_excluded(artist_name: str) -> bool:
        return artist_name.lower() in ExcludedArtists.excluded_artists
