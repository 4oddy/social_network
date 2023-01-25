from typing import Any


class ApplicationError(Exception):
    """ Base exception for all application business logic errors
        Inheritors must implement default_error_message property
    """

    def __init__(self, message=None, extra=None):
        super().__init__(message)
        self.message = message or self.default_error_message
        self.extra = dict() or extra

    @property
    def default_error_message(self) -> Any:
        raise NotImplementedError
