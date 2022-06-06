class APIErrorException(Exception):
    status_code: int
    description: str
    error_message: str

    def __init__(self, status_code: int | None = None, message: str | None = None):
        if status_code:
            self.status_code = status_code
        if message:
            self.error_message = message
        elif (
            not self.error_message
        ):  # if no error message provided description becomes also an error message
            self.error_message = self.description


class ConflictException(APIErrorException):
    status_code = 409
    description = "The request cannot be processed because of conflict"


class NotFoundException(APIErrorException):
    status_code = 404
    description = "Requested item does not exist"


class PoolDoesNotExistException(NotFoundException):
    description = "Requested pool does not exist"


class AccessDeniedException(APIErrorException):
    status_code = 403
    description = "Access to the requested resource has been denied"


class IncorrectInputException(APIErrorException):
    status_code = 400
    description = "Input data is incorrect"
