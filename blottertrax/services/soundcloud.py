import requests

from blottertrax.config import Config
from blottertrax.services.threshold_service import ThresholdService
from blottertrax.value_objects.parsed_submission import ParsedSubmission
from blottertrax.value_objects.service_result import ThresholdServiceResult


class Soundcloud(ThresholdService):
    config: Config = Config()
    Threshold = 500000
    
    def get_service_result(self, parsed_submission: ParsedSubmission) -> ThresholdServiceResult:
        url = parsed_submission.get_final_url()
        if 'soundcloud.com' not in url:
            return ThresholdServiceResult(False, 0, 0, '')

        response = requests.get(
            'https://api.soundcloud.com/resolve.json?url=' + url + '&client_id=' + self.config.SOUNDCLOUD_KEY
        )

        if response.status_code != 200:
            return ThresholdServiceResult(False, 0, 0, '')

        data = response.json()

        return ThresholdServiceResult(data['playback_count'] > self.Threshold, data['playback_count'], self.Threshold,
                                      'Soundcloud plays')

    def requires_fully_parsed_submission(self):
        return False
