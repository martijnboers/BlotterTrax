from blottertrax.value_objects.parsed_submission import ParsedSubmission


class TitleParser:

    # Calls the main parsing methods and returns a parsed submission if successful.
    @classmethod
    def create_parsed_submission_from_submission(cls, submission) -> ParsedSubmission:
        try:
            artist = cls.get_artist_name_from_submission_title(submission.title)
            song = cls.get_song_name_from_submission_title(submission.title, artist)
            return ParsedSubmission(True, submission.url, artist[0], artist[1], song)  # , submission.id)
        except Exception:
            # On any failures, pass back a ParsedSubmission object with success flag of False
            return ParsedSubmission(False, submission.url)

    # iterate and remove prioritized dash. Second variable denotes whether looking for artist (0) or song (1)
    @staticmethod
    def remove_prioritized_dash(post_title, is_song):
        dash_char = ['-', '—', '–']
        # iterate each of the set dash characters
        for dash in dash_char:
            # First check for instances of the dash character appearing twice in a row. We want to prioritize this
            if (dash + dash) in post_title:
                parsed = post_title.split(dash + dash, 1)[is_song].strip()  # splits off the double dash and strips
                # Will return "a-B (FEAT c) -" for artist  and "- d [e/f](g)" for song
                return parsed

        # if no instance of dash character appearing twice in a row just split first dash instance.
        for dash in dash_char:
            if dash in post_title:
                parsed = post_title.split(dash, 1)[is_song].strip()
                return parsed

        raise LookupError

    # Gets artist name from title.
    @classmethod
    def get_artist_name_from_submission_title(cls, post_title):
        # let's start with a sample title "a-B (FEAT c) - -- - d [e/f](g)"
        artist = cls.remove_prioritized_dash(post_title, 0)

        # get feature artist if exists
        lower_title = post_title.lower()  # makes a separate lowercase var for case insensitive comparison.
        feature_artist = None

        for feature in ['feat.', 'ft.', 'feature', 'featuring', ' feat ', '(feat ']:
            if feature not in lower_title:  # this will be false for "(feat " because we lowercased
                continue

            # we don't want to actually get the lowercase artist names, so we get the index.
            feat_index = lower_title.index(feature)

            # remove featuring from artist if exists (do nothing if featuring is in song side)
            if len(artist) > feat_index:
                artist = artist[:feat_index].strip()  # Removes all after feat_index and strips, artist = "a-B"
                # remove potential trailing parenthesis, mostly precaution
                if artist[len(artist) - 1] == '(':
                    artist = artist.rsplit('(', 1)[0].strip()

            # add the length of the actual feature comparison string so we can split after it.
            feat_index += len(feature)

            # isolate featuring artist
            # removes all before feat_index and strips, feature_artist = "c) - -- - d [e/f](g)"
            feature_artist = post_title[feat_index:].strip()
            break

        # find various trailing characters to trim down featuring artist
        if feature_artist is not None:
            for end_char in [' -', ' —', ')', '[']:
                if end_char in feature_artist:
                    feature_artist = feature_artist.split(end_char)[0]  # first = "c)", then = "c"

        if feature_artist is not None:
            feature_artist = feature_artist.strip()

        return_list = [artist, feature_artist]

        # if return_list[0] is none there is no way to trust whatever is in [1] anyway as the post title is a mess.
        if return_list[0] is not None:
            return return_list

        raise LookupError

    @classmethod
    def get_song_name_from_submission_title(cls, post_title, artist_name):

        left_tag = ["[", "(", "<"]

        post_title = post_title.lower()  # only compare lowercase because that's all that's needed.

        # remove artist
        # "a-b (feat c) - -- - d [e/f](g)" -> " (feat c) - -- - d [e/f](g)"
        post_title = post_title.split(artist_name[0].lower(), 1)[1]

        # remove featuring tag if exists
        for feature in ['feat.', 'ft.', 'feature', 'featuring', ' feat ', '(feat ']:
            if feature not in post_title:  # lowercased, so (feat will be false.
                continue

            # create a variable with all on both sides of featuring, because it may be before or after song.
            post_split = post_title.rsplit(feature, 1)

            # decide if song to left or right of featuring. in our case " ".strip == ""
            if post_split[0].strip() != "" and post_split[0].strip() not in left_tag:
                post_title = post_split[0].strip()
            else:
                post_title = post_split[1].strip()  # "c) - -- - d [e/f](g)"
                post_title = post_title.rsplit(artist_name[1].lower(), 1)[1].strip()  # ") - -- - d [e/f](g)"
                # remove potential trailing parenthesis
                if post_title[0] == ')':
                    post_title = post_title.split(')', 1)[1]  # " - -- - d [e/f](g)"

            break

        post_title = post_title.strip()  # "- -- - d [e/f](g)"

        post_title = cls.remove_prioritized_dash(post_title, 1)  # "- d [e/f](g)"

        post_split = post_title.split(None, 1)  # split by first whitespace, our case ["-", "d [e/f](g)"]

        if len(post_split) == 0:  # if 0 then there is no song title to be found. Prevents errors in future checks.
            return None

        # if first character is dash and split <= 2 chars,
        # assume the formatting was bad and remove until first whitespace
        if post_split[0][0] == '-' and len(post_split[0]) <= 2:
            post_title = post_split[1]  # "d [e/f](g)"

        # remove any thing after left tags.
        for tag in left_tag:
            post_title = post_title.split(tag, 1)[0]  # "d "

        return post_title.strip()  # "d"
