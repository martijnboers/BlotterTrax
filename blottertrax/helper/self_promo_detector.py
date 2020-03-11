from blottertrax.value_objects.parsed_submission import ParsedSubmission


class SelfPromoDetector:
    @staticmethod
    def is_self_promo(parsed_submission: ParsedSubmission, raw_submission) -> bool:

        if not parsed_submission.success:
            return False

        poster_name = raw_submission.author.name.lower().replace("_", "").replace("-", "")
        artist_name = parsed_submission.artist.lower().replace(" ", "").replace("_", "").replace("-", "")

        print(artist_name)

        # Super simple check.  Ensure the posters name does not appear in the name of the artist or the featured artist.
        # TODO: Add additional checks. https://github.com/martijnboers/BlotterTrax/issues/26
        if artist_name in poster_name:
            return True

        if poster_name in artist_name:
            return True

        if parsed_submission.featuring_artist is not None:
            feature_name = parsed_submission.featuring_artist.lower().replace(" ", "")
            if feature_name in poster_name:
                return True

            if poster_name in feature_name:
                return True

        return False
