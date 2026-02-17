"""Custom exceptions for the Nodela SDK."""

from typing import Any, Optional


class NodelaError(Exception):
    """Base exception for all Nodela SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(NodelaError):
    """Raised when authentication fails."""

    pass


class ValidationError(NodelaError):
    """Raised when request validation fails."""

    pass


class RateLimitError(NodelaError):
    """Raised when the API rate limit is exceeded."""

    pass


class NotFoundError(NodelaError):
    """Raised when a resource is not found."""

    pass


class ServerError(NodelaError):
    """Raised when the server returns a 5xx error."""

    pass


class NetworkError(NodelaError):
    """Raised when a network error occurs."""

    pass
