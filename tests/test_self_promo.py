from unittest import TestCase

from blottertrax.helper.self_promo_detector import SelfPromoDetector
from blottertrax.value_objects.parsed_submission import ParsedSubmission


class MockedSubmission:
    def __init__(self, author_name):
        self.author = type('', (), {})()
        self.author.name = author_name


class TestSelfPromo(TestCase):

    def test_it_should_detect_username_same_as_artist(self):
        parsed = ParsedSubmission(True, 'url', 'TestRedditor')
        sub = MockedSubmission("testredditor01rocks")
        self.assertTrue(SelfPromoDetector.is_self_promo(parsed, sub))

        parsed = ParsedSubmission(True, 'url', 'testredditor 01rocks')
        sub = MockedSubmission("TestRedditor")
        self.assertTrue(SelfPromoDetector.is_self_promo(parsed, sub))

    def test_it_should_detect_username_same_as_featured_artist(self):
        parsed = ParsedSubmission(True, 'url', 'NoMatch', 'redditor01rocks')
        sub = MockedSubmission("testredditor01rocks")
        self.assertTrue(SelfPromoDetector.is_self_promo(parsed, sub))

        parsed = ParsedSubmission(True, 'url', 'NoMatch', 'test redditor 01 rocks')
        sub = MockedSubmission("redditor01")
        self.assertTrue(SelfPromoDetector.is_self_promo(parsed, sub))

    def test_it_should_not_fail_on_failed_parsed_submission(self):
        parsed = ParsedSubmission(False, 'url')
        sub = MockedSubmission("testredditor01rocks")
        self.assertFalse(SelfPromoDetector.is_self_promo(parsed, sub))

    def test_it_should_fail_on_no_match(self):
        parsed = ParsedSubmission(True, 'url', 'Nedl2dinin')
        sub = MockedSubmission("Not_Ned l1inin")
        self.assertFalse(SelfPromoDetector.is_self_promo(parsed, sub))

    def test_it_should_work_with_spaces_and_dashes(self):
        parsed = ParsedSubmission(True, 'url', 'Test_Red_Ditor')
        sub = MockedSubmission("TestRedditor")
        self.assertTrue(SelfPromoDetector.is_self_promo(parsed, sub))

        parsed = ParsedSubmission(True, 'url', 'te_str-edd-itor 01rocks')
        sub = MockedSubmission("TestRedditor")
        self.assertTrue(SelfPromoDetector.is_self_promo(parsed, sub))
