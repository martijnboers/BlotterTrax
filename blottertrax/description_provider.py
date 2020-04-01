import musicbrainzngs

from blottertrax.config import Config
from blottertrax.exceptions.description_exception import DescriptionException
from blottertrax.helper import templates
from blottertrax.helper.array_util import ArrayUtil
from blottertrax.value_objects.parsed_submission import ParsedSubmission


class DescriptionProvider:
    musicbrainz = None

    def __init__(self):
        config = Config()

        self.musicbrainz = musicbrainzngs
        self.musicbrainz.auth(config.MUSICBRAINZ_USER, config.MUSICBRAINZ_PASSWORD)
        self.musicbrainz.set_useragent("BlotterTrax", "0.1", "https://github.com/martijnboers/BlotterTrax")

    def get_reply(self, parsed_submission: ParsedSubmission) -> str:
        if parsed_submission.success is False:
            raise DescriptionException('DescriptionProvider requires the submission title')

        query = '"{}" AND artist:"{}"'.format(parsed_submission.track_title, parsed_submission.artist)
        result = self.musicbrainz.search_recordings(query=query, limit=1, )

        if result['recording-count'] == 0:
            raise DescriptionException('No recordings found for artist')

        recording = result['recording-list'][0]
        artist = self._get_artist_by_id(recording.get('artist-credit')[0]['artist']['id'])

        life_span_begin = ArrayUtil.safe_list_get(artist, '?', 'life-span', 'begin')
        life_span_end = ArrayUtil.safe_list_get(artist, 'now', 'life-span', 'end')
        has_life_span = (life_span_end != 'now' or life_span_begin != '?')
        has_tags = (ArrayUtil.safe_list_get(artist, False, 'tag-list') is not False)
        has_socials = (ArrayUtil.safe_list_get(artist, False, 'url-relation-list') is not False)

        if has_tags is False and has_socials is False:
            raise DescriptionException('Neither tags nor socials found, skipping')

        life_span = '' if has_life_span is False else '({} to {})'.format(life_span_begin, life_span_end)
        tags = ', '.join(map(lambda t: t['name'], artist['tag-list'][:5])) if has_tags else 'none'
        socials = ", ".join(map(format_network_to_friendly_name,
                                artist['url-relation-list'])) if has_socials else 'none'
                    

        return templates.musicbrainz_artist_info.strip().format(
            artist['name'],
            life_span,
            recording['title'],
            recording['release-list'][0]['date'],
            tags,
            socials,
            artist['id']
        )

    def _get_artist_by_id(self, artist_id: str):
        return self.musicbrainz.get_artist_by_id(
            id=artist_id, includes=['tags', 'ratings', 'annotation', 'url-rels', 'user-tags']
        )['artist']
    
    def format_network_to_friendly_name(self, info) -> str:
        social_network = ["twitter.com", "facebook.com", "instagram.com"]
        target = info['target']
        link_type = info['type']
        if link_type == 'social network':
            for domain in social_network:
                if domain in target:
                    link_type = domain.split(".")[0]
                    break
        return '[{}]({})'.format(link_type, '\)'.join(target.split(')'))
