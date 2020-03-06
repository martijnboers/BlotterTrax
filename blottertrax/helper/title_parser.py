import re

from blottertrax.value_objects.parsed_submission import ParsedSubmission


class TitleParser:

    @staticmethod
    def create_parsed_submission_from_submission(submission) -> ParsedSubmission:
        artist = None
        feature_artist = None
        song_title = None
        post_title = submission.title

        for dash in [' - ', ' — ', ' -- ', ' - - ', ' —— ']:
            if dash in post_title:
                split_result = post_title.split(dash)
                artist = split_result[0]
                song_title = split_result[1]

                break

        if artist is None:
            raise LookupError

        for feature in [' feat. ', ' ft. ', ' feature ', ' featuring ', ' feat ']:
            if feature not in post_title or artist is None:
                continue

            feat_index = post_title.index(feature)

            # remove featuring from artist if exists
            if len(artist) > feat_index:
                artist = artist[:feat_index].strip()

            feat_index += len(feature)

            # isolate featuring artist
            feature_artist = post_title[feat_index:].strip()

            for end_char in [' -', ')', '[', ' —']:
                if end_char in feature_artist:
                    split_result = feature_artist.split(end_char)
                    feature_artist, song_title = split_result

                    break

        if song_title is None:
            raise LookupError

        # Remove everything between () and []
        song_title = re.sub(r"\(.*\)", "", song_title)
        song_title = re.sub(r"[.*]", "", song_title)
        song_title = song_title.strip()

        if artist is not None:
            return ParsedSubmission(artist, feature_artist, song_title, submission.url)

        raise LookupError
