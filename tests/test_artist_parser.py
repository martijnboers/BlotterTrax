from unittest import TestCase

from blottertrax.helper.title_parser import TitleParser


class TestBlotterTrax(TestCase):

    def test_extract_artist_post_title(self):
        submissions = [
            ('B12 - Infinite Lites (Original Mix) ', 'B12', None),
            ('Floating Points - Last Bloom ', 'Floating Points', None),
            ('Empty Spaces -- Một Cuộc Sống Khác [Vietnamese/Alternative] (2019) ', 'Empty Spaces', None),
            ('007Bonez & Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro'),
            ('007Bonez featuring Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro'),
            ('007Bonez feat Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez feat Adro', None),
            ('007Bonez feat. Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro'),
            ('Teen Suicide — Haunt Me x3 [indie rock] (2014)', 'Teen Suicide', None),
            ("upsammy - Another Place - Nous'klaer 011", 'upsammy', None),
            ('ガールズロックバンド革命 - CHANGE', 'ガールズロックバンド革命', None),
            ('Blume - popo -- 溺レル', 'Blume - popo', None)
        ]
        for submission_title, artist, featuring_artist in submissions:
            title = TitleParser.get_artist_name_from_submission_title(submission_title)

            self.assertEqual(artist, title[0])
            self.assertEqual(featuring_artist, title[1])