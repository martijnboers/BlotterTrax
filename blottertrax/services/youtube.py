from typing import List
from urllib import parse
from urllib.parse import urlparse

import googleapiclient.discovery
import googleapiclient.errors

from blottertrax.config import Config
from blottertrax.services.threshold_service import ThresholdService
from blottertrax.value_objects.parsed_submission import ParsedSubmission
from blottertrax.value_objects.service_result import ThresholdServiceResult


class Youtube(ThresholdService):
    config: Config = Config()
    youtubeClient = None
    threshold = 1_000_000
    youtubeUrls: List[str] = ['youtube.com', 'youtube.be', 'www.youtube.com', 'youtu.be']

    def __init__(self):
        api_service_name = "youtube"
        api_version = "v3"

        self.youtubeClient = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.config.YT_KEY, cache_discovery=False)

    def get_service_result(self, parsed_submission: ParsedSubmission) -> ThresholdServiceResult:
        """
        Get the v query from the url and use it to query for Youtube review statistics
        """
        final_url = urlparse(parsed_submission.get_final_url())

        if final_url.netloc not in self.youtubeUrls:
            return ThresholdServiceResult.error()

        query = parse.parse_qs(parse.urlsplit(final_url.geturl()).query)

        request = self.youtubeClient.videos().list(
            part="statistics",
            id=query['v'][0]
        )
        response = request.execute()
        view_count = int(response['items'][0]['statistics']['viewCount'])

        return ThresholdServiceResult(view_count > self.threshold, view_count, self.threshold, 'YouTube plays')

    def requires_fully_parsed_submission(self):
        return False
