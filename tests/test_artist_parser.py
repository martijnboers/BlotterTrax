from unittest import TestCase

from blottertrax.helper.title_parser import TitleParser

class MockedSubmission:
    def __init__(self, title):
        self.title = title
        self.url = 'https://url.com'
        self.id = '7188'

class TestBlotterTrax(TestCase):

    def test_extract_artist_post_title(self):
        submissions = [
            ('B12 - Infinite Lites (Original Mix) ', 'B12', None, 'Infinite Lites'),
            ('Floating Points - Last Bloom ', 'Floating Points', None, 'Last Bloom'),
            ('Empty Spaces -- Một Cuộc Sống Khác [Vietnamese/Alternative] (2019) ', 'Empty Spaces', None, 'Một Cuộc Sống Khác'),
            ('007Bonez featuring Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('007Bonez feat Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('007Bonez feat. Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('007Bonez - Motion featuring Adro [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('007Bonez (featuring Adro) - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'Motion'),
            ('Teen Suicide — Haunt Me x3 [indie rock] (2014)', 'Teen Suicide', None, 'Haunt Me x3'),
            ("upsammy - Another Place - Nous'klaer 011", 'upsammy', None, "Another Place - Nous'klaer 011"),
            ('ガールズロックバンド革命 - CHANGE', 'ガールズロックバンド革命', None, 'CHANGE'),
            ('Blume - popo -- 溺レル', 'Blume - popo', None, '溺レル'),
            ('Simon & Garfunkel - The Sound of Silence', 'Simon & Garfunkel', None, 'The Sound of Silence')
        ]
        for submission_title, artist, featuring_artist, song_name in submissions:
            title = TitleParser.get_artist_name_from_submission_title(submission_title)
            song = TitleParser.get_song_name_from_submission_title(submission_title, title)

            self.assertEqual(artist, title[0])
            self.assertEqual(featuring_artist, title[1])
            self.assertEqual(song_name.lower(), song)
