from unittest import TestCase

from blottertrax.helper.excluded_artists import ExcludedArtists


class TestExcludedArtists(TestCase):

    def test_it_should_know_excluded_artists(self):
        self.assertTrue(ExcludedArtists.is_excluded('various artists'))

    def test_it_should_know_excluded_artists_case_insensitive(self):
        self.assertTrue(ExcludedArtists.is_excluded('Anonymous'))
