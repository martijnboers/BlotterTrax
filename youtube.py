import os
from typing import List
from urllib import parse

import googleapiclient.discovery
import googleapiclient.errors

from config import Config

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


class Youtube:
    config: Config = Config()
    youtubeClient = None
    threshold = 500000
    youtubeUrls: List[str] = ['youtube.com', 'youtube.be', 'www.youtube.com']

    def __init__(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        self.youtubeClient = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.config.YT_KEY)

    def exceedsThreshold(self, parsedurl):
        if parsedurl.netloc not in self.youtubeUrls:
            return

        query = parse.parse_qs(parse.urlsplit(parsedurl.geturl()).query)

        request = self.youtubeClient.videos().list(
            part="statistics",
            id=query['v'][0]
        )
        response = request.execute()
        viewcount = int(response['items'][0]['statistics']['viewCount'])

        return {'exceeds': viewcount > self.threshold, 'count': viewcount, 'threshold': self.threshold}
