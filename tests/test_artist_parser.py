from unittest import TestCase

from blottertrax.helper.title_parser import TitleParser


class TestBlotterTrax(TestCase):

    def test_extract_artist_post_title(self):
        submissions = [
            ('B12 - Infinite Lites (Original Mix) ', 'B12', None, 'Infinite Lites'),
            ('Floating Points - Last Bloom ', 'Floating Points', None, 'Last Bloom'),
            ('Empty Spaces -- Một Cuộc Sống Khác [Vietnamese/Alternative] (2019) ', 'Empty Spaces', None, 'Một Cuộc Sống Khác'),
            ('007Bonez & Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('007Bonez featuring Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('007Bonez feat Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez feat Adro', None, 'Motion'),
            ('007Bonez feat. Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('Teen Suicide — Haunt Me x3 [indie rock] (2014)', 'Teen Suicide', None, 'Haunt Me x3'),
            ("upsammy - Another Place - Nous'klaer 011", 'upsammy', None, "Another Place - Nous'klaer 011"),
            ('ガールズロックバンド革命 - CHANGE', 'ガールズロックバンド革命', None, 'CHANGE'),
        ]
        for submission_title, artist, featuring_artist, song_title in submissions:
            title = TitleParser.create_parsed_submission_from_post_title(submission_title)

            self.assertEqual(artist, title.artist)
            self.assertEqual(featuring_artist, title.featuring_artist)
            # self.assertEqual(song_title, title.track_title)
