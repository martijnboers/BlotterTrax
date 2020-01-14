import os
import json

import googleapiclient.discovery
import googleapiclient.errors

from config import Config

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


class Youtube:
    config = Config()

    def video(self, youtubeId):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.config.YT_KEY)

        request = youtube.videos().list(
            part="statistics",
            id=youtubeId
        )
        response = request.execute()

        return int(response['items'][0]['statistics']['viewCount'])
