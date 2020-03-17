class ThresholdServiceResult:
    exceeds_threshold: bool
    listeners_count: int
    threshold: int
    service_name: str

    def __init__(self, exceeds_threshold: bool, listeners_count: int, threshold: int, service_name: str):
        self.exceeds_threshold = exceeds_threshold
        self.listeners_count = listeners_count
        self.threshold = threshold
        self.service_name = service_name
