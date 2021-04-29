from datetime import date

from blottertrax.config import Config
from blottertrax.value_objects.service_result import ThresholdServiceResult


# Be sure to instantiate a new one for every post!
# TODO: Would we rather keep one around and just have a "reset" function?
class OverallThresholdService:
    config: Config = Config()
    Threshold = config.APP.OVERALL_LISTEN_THRESHOLD
    running_count = 0

    def get_service_result(self) -> ThresholdServiceResult:
        result = ThresholdServiceResult(self.running_count > self.Threshold, self.running_count, self.Threshold,
                                        'Plays across known media sites')
        return result

    def add_service_result(self, result: ThresholdServiceResult):
        self.running_count += result.listeners_count

    @staticmethod
    def is_cheat_day():
        return date.today().weekday() == 0
