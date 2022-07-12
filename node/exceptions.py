class APIException(Exception):
    status_code: int
    error_message: str | None = None

    def __init__(self, error_message: str | None = None):
        if error_message:
            self.error_message = error_message
        if not self.error_message:
            raise RuntimeError("API exception does not have error message.")


class ConflictException(APIException):
    status_code = 409
    error_message = "The request cannot be processed because of conflict."


class NotFoundException(APIException):
    status_code = 404
    error_message = "Requested item does not exist."


class PoolDoesNotExistException(NotFoundException):
    error_message = "Pool does not exist."


class SignatureNotFoundException(NotFoundException):
    error_message = "Signature does not exist."


class AccessDeniedException(APIException):
    status_code = 403
    error_message = "Access to the requested resource has been denied."


class InvalidMasterKeyException(AccessDeniedException):
    error_message = "Invalid master key."


class InvalidWriterKeyException(AccessDeniedException):
    error_message = "Invalid writer key."


class InvalidReaderKeyException(AccessDeniedException):
    error_message = "Invalid reader key."


class InvalidSignatureKeyException(AccessDeniedException):
    error_message = "Invalid signature key."


class UnprocessableEntityException(APIException):
    status_code = 422
    error_message = "Unprocessable entity."


class InternalServerErrorException(APIException):
    status_code = 500
    error_message = "Internal server error."
