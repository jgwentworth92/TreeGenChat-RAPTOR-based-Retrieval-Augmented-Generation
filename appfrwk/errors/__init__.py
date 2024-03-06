"""
Custom exceptions for the application
"""

from fastapi import HTTPException, status

class AppError(Exception):
    """
    Base class for exceptions in this module.
    """
    pass

class InvalidRequestError(AppError):
    pass

class InvalidAPIKeyError(InvalidRequestError):
    def __init__(self, message):
        super().__init__(message)

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)

class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )