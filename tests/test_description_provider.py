import unittest
from blottertrax.description_provider import DescriptionProvider


class MyTestCase(unittest.TestCase):
    def test_format_network_to_friendly_name(self):

        networks = [
            ('social network', 'https://facebook.com/linkedpage', '[facebook](https://facebook.com/linkedpage)'),
            ('social network', 'https://twitter.com/linkedpage', '[twitter](https://twitter.com/linkedpage)'),
            ('social network', 'https://instagram.com/linkedpage', '[instagram](https://instagram.com/linkedpage)'),
            ('discogs', 'https://discogs.com/linkedpage', '[discogs](https://discogs.com/linkedpage)'),
            (
                'some other database',
                'https://some-other-database.com/linkedpage',
                '[some other database](https://some-other-database.com/linkedpage)'
            ),
            (
                'wikipedia',
                'https://en.wikipedia.org/wiki/Caravan_(band)',
                r'[wikipedia](https://en.wikipedia.org/wiki/Caravan_\(band\))'
            ),
        ]
        for network_type, target, expected in networks:
            formatted = DescriptionProvider.format_network_to_friendly_name({
                'target': target,
                'type': network_type
            })

            self.assertEqual(expected, formatted)
