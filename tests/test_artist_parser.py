from unittest import TestCase

from blottertrax.helper.title_parser import TitleParser


class MockedSubmission:
    def __init__(self, title):
        self.title = title
        self.url = 'https://url.com'


class TestBlotterTrax(TestCase):

    def test_extract_artist_post_title(self):
        submissions = [
            ('B12 - Infinite Lites (Original Mix) ', 'B12', None, 'infinite lites'),
            ('Floating Points - Last Bloom ', 'Floating Points', None, 'last bloom'),
            ('Floating Points-Last Bloom ', 'Floating Points', None, 'last bloom'),
            ('Floating Points -- Last Bloom ', 'Floating Points', None, 'last bloom'),
            ('Floating Points feat. Boombox -- Last Bloom ', 'Floating Points', 'Boombox', 'last bloom'),
            ('Floating Points --Last Bloom ', 'Floating Points', None, 'last bloom'),
            ('Floating Points feat. Testing - Last Bloom ', 'Floating Points', 'Testing', 'last bloom'),
            ('Floating Points   -- Last Bloom ', 'Floating Points', None, 'last bloom'),
            ('Empty Spaces -- Một Cuộc Sống Khác [Vietnamese/Alternative] (2019) ', 'Empty Spaces', None,
             'một cuộc sống khác'),
            ('007Bonez featuring Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'motion'),
            ('007Bonez feat Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'motion'),
            ('007Bonez feat. Adro - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'motion'),
            ('007Bonez - Motion featuring Adro [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'motion'),
            ('007Bonez (featuring Adro) - Motion [Hip-Hop / Rap] (2019)', '007Bonez', 'Adro', 'motion'),
            ('Teen Suicide — Haunt Me x3 [indie rock] (2014)', 'Teen Suicide', None, 'haunt me x3'),
            ("upsammy - Another Place - Nous'klaer 011", 'upsammy', None, "another place - nous'klaer 011"),
            ('ガールズロックバンド革命 - CHANGE', 'ガールズロックバンド革命', None, 'change'),
            ('Blume - popo -- 溺レル', 'Blume - popo', None, '溺レル'),
            ('Simon & Garfunkel - The Sound of Silence', 'Simon & Garfunkel', None, 'the sound of silence'),
            ('Badly formatted title -', 'Badly formatted title', None, None),
            ('Another badly formatted title -    ', 'Another badly formatted title', None, None),
            ('a-B (FEAT c) - -- - d [e/f](g)', 'a-B', 'c', 'd'),
            ("Meers – Don't Tell The Circus [Indie Pop] (2020)", 'Meers', None, "don't tell the circus")
        ]
        for submission_title, artist, featuring_artist, song_title in submissions:
            title = TitleParser.create_parsed_submission_from_submission(MockedSubmission(submission_title))

            self.assertEqual(artist, title.artist)
            self.assertEqual(featuring_artist, title.featuring_artist)
            self.assertEqual(song_title, title.track_title)
