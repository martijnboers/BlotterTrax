from unittest import TestCase

from title_parser import TitleParser


class TestBlotterTrax(TestCase):

    def test_extract_artist_post_title(self):
        submissions = [
            ('B12 - Infinite Lites (Original Mix) ', 'B12'),
            ('Floating Points - Last Bloom ', 'Floating Points'),
            ('Empty Spaces -- Một Cuộc Sống Khác [Vietnamese/Alternative] (2019) ', 'Empty Spaces'),
            ('007Bonez & Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez'),
            ('007Bonez featuring Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez'),
            ('007Bonez feat Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez'),
            ('007Bonez feat. Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez'),
            ('Teen Suicide — Haunt Me x3 [indie rock] (2014)', 'Teen Suicide'),
            ("upsammy - Another Place - Nous'klaer 011", 'upsammy'),
        ]
        for submission_title, artist in submissions:
            title = TitleParser._get_artist_name_from_submission_title(submission_title)
            prio_artist = TitleParser._get_prioritized_artist(title)

            self.assertEqual(artist, prio_artist)
