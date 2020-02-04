import os
from typing import List
from urllib import parse

import googleapiclient.discovery
import googleapiclient.errors

from config import Config
from serviceresult import ServiceResult

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


class Youtube:
    config: Config = Config()
    youtubeClient = None
    threshold = 500_000
    youtubeUrls: List[str] = ['youtube.com', 'youtube.be', 'www.youtube.com']

    def __init__(self):
        api_service_name = "youtube"
        api_version = "v3"

        self.youtubeClient = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.config.YT_KEY)

    def get_service_result(self, parsed_url) -> ServiceResult:
        """
        Get the v query from the url and use it to query for Youtube review statistics
        """
        if parsed_url.netloc not in self.youtubeUrls:
            return ServiceResult(False, 0, 0, '')

        query = parse.parse_qs(parse.urlsplit(parsed_url.geturl()).query)

        request = self.youtubeClient.videos().list(
            part="statistics",
            id=query['v'][0]
        )
        response = request.execute()
        view_count = int(response['items'][0]['statistics']['viewCount'])

        return ServiceResult(view_count > self.threshold, view_count, self.threshold, 'YouTube plays')
