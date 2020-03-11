from unittest import TestCase

from blottertrax.helper.excluded_artists import ExcludedArtists
from blottertrax.value_objects.parsed_submission import ParsedSubmission


class TestExcludedArtists(TestCase):

    def test_it_should_know_excluded_artists(self):
        self.assertTrue(ExcludedArtists.is_excluded(ParsedSubmission(True, 'various artists', '', '', 'url')))

    def test_it_should_know_excluded_artists_case_insensitive(self):
        self.assertTrue(ExcludedArtists.is_excluded(ParsedSubmission(True, 'Anonymous', '', '', 'url')))
