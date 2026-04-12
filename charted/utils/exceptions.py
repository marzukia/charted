class InvalidValue(Exception):
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value
        super().__init__(self.__str__())

    def __str__(self):
        return f"'{self.value}' is not a valid value for '{self.name}'"


class ChartError(Exception):
    """Base exception for chart-related errors."""
    pass


class NoDataError(ChartError):
    """Raised when no data is provided to a chart."""
    pass


class VectorLengthMismatchError(ChartError):
    """Raised when vectors have mismatched lengths."""
    pass
