import requests

from blottertrax.config import Config
from blottertrax.services.threshold_service import ThresholdService
from blottertrax.value_objects.parsed_submission import ParsedSubmission
from blottertrax.value_objects.service_result import ThresholdServiceResult


class Soundcloud(ThresholdService):
    config: Config = Config()
    Threshold = 500000

    def get_service_result(self, parsed_submission: ParsedSubmission) -> ThresholdServiceResult:
        # Follow URL to the end location in case of URL shorteners
        session = requests.Session()  # so connections are recycled
        resp = session.head(parsed_submission.url, allow_redirects=True)
        final_url = resp.url

        if 'soundcloud.com' not in final_url:
            return ThresholdServiceResult(False, 0, 0, '')

        response = requests.get(
            'https://api.soundcloud.com/resolve.json?url=' +
            parsed_submission.url +
            '&client_id=' +
            self.config.SOUNDCLOUD_KEY)

        if response.status_code != 200:
            return ThresholdServiceResult(False, 0, 0, '')

        data = response.json()

        return ThresholdServiceResult(data['playback_count'] > self.Threshold, data['playback_count'], self.Threshold,
                             'Soundcloud plays')

    def requires_fully_parsed_submission(self):
        return False
