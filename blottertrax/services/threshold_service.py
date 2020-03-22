from blottertrax.value_objects.parsed_submission import ParsedSubmission
from blottertrax.value_objects.service_result import ThresholdServiceResult
from abc import ABC, abstractmethod


class ThresholdService(ABC):
    @abstractmethod
    def get_service_result(self, parsed_submission: ParsedSubmission) -> ThresholdServiceResult:
        pass

    @abstractmethod
    def requires_fully_parsed_submission(self):
        pass
