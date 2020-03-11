from blottertrax.value_objects.parsed_submission import ParsedSubmission


class ExcludedArtists:
    excluded_artists: list = [
        'various artists',
        'anonymous',
        'va',
        'various'
    ]

    @staticmethod
    def is_excluded(parsed_submission: ParsedSubmission) -> bool:
        return parsed_submission.success is True and parsed_submission.artist.lower() in ExcludedArtists.excluded_artists
