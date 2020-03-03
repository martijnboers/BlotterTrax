class TitleParser:

    @staticmethod
    def get_prioritized_artist(artist_list):
        if artist_list[1] is None:
            return artist_list[0]

        return artist_list[1]

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

        for feature in ['feat.', 'ft.', 'feature', 'featuring', '&']:
            if feature in lower_title:
                feat_index = lower_title.index(feature)

                # remove featuring from artist if exists
                if len(artist) > feat_index:
                    artist = artist[:feat_index].strip()

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

        left_tag = ["[", "(", "<", "<<"]
        right_tag = ["]", ")", ">", ">>"]

        artist_name = artist_name.lower()
        post_title = post_title.lower()

        # Remove year and genre tags from post
        for i in range(2):

            post_title = post_title.strip()

            lastChar = post_title[len(post_title) - 1]

            if (lastChar not in right_tag):
                return

            curChar = right_tag.index(lastChar)

            if (left_tag[curChar] not in post_title):
                return

            post_title = post_title.rsplit(left_tag[curChar], 1)[0]

        # remove artist
        post_title = post_title.rsplit(artist_name, 1)[1]

        post_title = post_title.strip().split(None, 1)[1]

        # remove featuring tag if exists
        for feature in ['&', 'feat.', 'featuring', 'feature', 'ft.']:
            if (feature not in post_title):
                continue

            postSplit = post_title.rsplit(feature, 1)

            if (postSplit[0] is not ""):
                post_title = postSplit[0]

            break

        post_title.strip()

        return post_title