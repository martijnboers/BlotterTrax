from blottertrax.value_objects.parsed_submission import ParsedSubmission

class TitleParser:

    @staticmethod
    def create_parsed_submission_from_submission(submission) -> ParsedSubmission:
        artist = TitleParser.get_artist_name_from_submission_title(submission.title)
        if artist[0] is not None:
            song = TitleParser.get_song_name_from_submission_title(submission.title, artist)
            return ParsedSubmission(artist[0], artist[1], song, submission.url, submission.id)

        raise LookupError

    @staticmethod
    def get_prioritized_artist(parsed_submission):
        if parsed_submission.featuring_artist is None:
            return parsed_submission.artist

        return parsed_submission.artist

    @staticmethod
    def get_artist_name_from_submission_title(post_title):
        # get main artist
        dash_char = ['-', '—']
        double_dash = False
        artist = None
        for dash in dash_char:
            if (dash + dash) in post_title:
                artist = post_title.split(dash + dash)[0].strip()
                double_dash = True
                break

        if double_dash is False:
            for dash in dash_char:
                if dash in post_title:
                    artist = post_title.split(dash)[0].strip()
                    break

        # get feature artist if exists
        lower_title = post_title.lower()
        feature_artist = None

        for feature in ['feat.', 'ft.', 'feature', 'featuring', ' feat ', '(feat ']:
            if feature in lower_title:
                feat_index = lower_title.index(feature)

                # remove featuring from artist if exists
                if len(artist) > feat_index:
                    artist = artist[:feat_index].strip()
                    # remove potential trailing parenthesis
                    if artist[len(artist) - 1] == '(':
                        artist = artist.rsplit('(', 1)[0].strip()

                feat_index += len(feature)

                # isolate featuring artist
                feature_artist = post_title[feat_index:].strip()
                break

        # further process if found
        if feature_artist is not None:
            for end_char in [' -', ')', '[', ' —']:
                if end_char in feature_artist:
                    feature_artist = feature_artist.split(end_char)[0]

        if feature_artist is not None:
            feature_artist = feature_artist.strip()

        return_list = [artist, feature_artist]

        # if return_list[0] is none there is no way to trust whatever is in [1] anyway as the post title is a mess.
        if return_list[0] is not None:
            return return_list

        raise LookupError

    @staticmethod
    def get_song_name_from_submission_title(post_title, artist_name):

        left_tag = ["[", "(", "<"]

        post_title = post_title.lower()

        # remove artist
        post_title = post_title.rsplit(artist_name[0].lower(), 1)[1].strip()

        # remove featuring tag if exists
        for feature in ['&', 'feat.', 'featuring', 'feature', 'ft.']:
            if (feature not in post_title):
                continue

            post_split = post_title.rsplit(feature, 1)

            if post_split[0] != "" and post_split[0] not in left_tag:
                post_title = post_split[0]
            else:
                post_title = post_title.split(feature, 1)[1].strip()
                post_title = post_title.rsplit(artist_name[1].lower(), 1)[1].strip()
                # remove potential trailing parenthesis
                if post_title[0] == ')':
                    post_title = post_title.split(')', 1)[1]

            break

        post_title = post_title.strip().split(None, 1)[1]

        for tag in left_tag:
            post_title = post_title.split(tag, 1)[0]

        return post_title.strip()
