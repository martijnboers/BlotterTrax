import requests

from blottertrax.config import Config
from blottertrax.value_objects.parsed_submission import ParsedSubmission
from blottertrax.value_objects.service_result import ServiceResult


class Soundcloud:
    config: Config = Config()
    Threshold = 500000

    def get_service_result(self, parsed_submission: ParsedSubmission) -> ServiceResult:
        url = parsed_submission.get_final_url()
        if 'soundcloud.com' not in url:
            return ServiceResult(False, 0, 0, '')

        response = requests.get(
            'https://api.soundcloud.com/resolve.json?url=' + url + '&client_id=' + self.config.SOUNDCLOUD_KEY
        )

        if response.status_code != 200:
            return ServiceResult(False, 0, 0, '')

        data = response.json()

        return ServiceResult(data['playback_count'] > self.Threshold, data['playback_count'], self.Threshold,
                             'Soundcloud plays')
