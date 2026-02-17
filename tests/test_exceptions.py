"""Unit tests for exception classes."""

from typing import Any, Dict

import pytest

from nodela.exceptions import (
    AuthenticationError,
    NetworkError,
    NodelaError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestNodelaError:
    """Test cases for the base NodelaError exception."""

    def test_basic_initialization(self) -> None:
        """Test basic error initialization with just a message."""
        error = NodelaError("Test error message")
        assert str(error) == "Test error message"
        assert error.status_code is None
        assert error.response is None

    def test_initialization_with_status_code(self) -> None:
        """Test error initialization with status code."""
        error = NodelaError("Test error", status_code=400)
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response is None

    def test_initialization_with_response(self) -> None:
        """Test error initialization with response data."""
        response_data: Dict[str, Any] = {"error": "details", "code": "ERR_001"}
        error = NodelaError("Test error", status_code=400, response=response_data)
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response == response_data

    def test_initialization_with_all_params(self) -> None:
        """Test error initialization with all parameters."""
        response_data: Dict[str, str] = {"message": "Detailed error"}
        error = NodelaError("Test error", status_code=500, response=response_data)
        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.response == response_data

    def test_is_exception_instance(self) -> None:
        """Test that NodelaError is an Exception instance."""
        error = NodelaError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, NodelaError)


class TestAuthenticationError:
    """Test cases for AuthenticationError."""

    def test_inheritance(self) -> None:
        """Test that AuthenticationError inherits from NodelaError."""
        error = AuthenticationError("Auth failed")
        assert isinstance(error, NodelaError)
        assert isinstance(error, AuthenticationError)

    def test_with_status_code(self) -> None:
        """Test AuthenticationError with status code 401."""
        error = AuthenticationError("Invalid API key", status_code=401)
        assert str(error) == "Invalid API key"
        assert error.status_code == 401

    def test_with_response_data(self) -> None:
        """Test AuthenticationError with response data."""
        response: Dict[str, str] = {"error": "unauthorized"}
        error = AuthenticationError("Auth failed", status_code=401, response=response)
        assert error.response == response


class TestValidationError:
    """Test cases for ValidationError."""

    def test_inheritance(self) -> None:
        """Test that ValidationError inherits from NodelaError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, NodelaError)
        assert isinstance(error, ValidationError)

    def test_with_status_code(self) -> None:
        """Test ValidationError with status codes 400 or 422."""
        error_400 = ValidationError("Bad request", status_code=400)
        assert error_400.status_code == 400

        error_422 = ValidationError("Unprocessable entity", status_code=422)
        assert error_422.status_code == 422

    def test_with_validation_details(self) -> None:
        """Test ValidationError with validation details in response."""
        response: Dict[str, Any] = {
            "errors": [
                {"field": "email", "message": "Invalid email format"},
                {"field": "amount", "message": "Must be positive"},
            ]
        }
        error = ValidationError("Validation failed", status_code=422, response=response)
        assert error.response == response


class TestRateLimitError:
    """Test cases for RateLimitError."""

    def test_inheritance(self) -> None:
        """Test that RateLimitError inherits from NodelaError."""
        error = RateLimitError("Rate limit exceeded")
        assert isinstance(error, NodelaError)
        assert isinstance(error, RateLimitError)

    def test_with_status_code(self) -> None:
        """Test RateLimitError with status code 429."""
        error = RateLimitError("Too many requests", status_code=429)
        assert str(error) == "Too many requests"
        assert error.status_code == 429

    def test_with_retry_after(self) -> None:
        """Test RateLimitError with retry-after information."""
        response: Dict[str, Any] = {"retry_after": 60}
        error = RateLimitError("Rate limited", status_code=429, response=response)
        assert error.response == response
        assert error.response["retry_after"] == 60


class TestNotFoundError:
    """Test cases for NotFoundError."""

    def test_inheritance(self) -> None:
        """Test that NotFoundError inherits from NodelaError."""
        error = NotFoundError("Resource not found")
        assert isinstance(error, NodelaError)
        assert isinstance(error, NotFoundError)

    def test_with_status_code(self) -> None:
        """Test NotFoundError with status code 404."""
        error = NotFoundError("Invoice not found", status_code=404)
        assert str(error) == "Invoice not found"
        assert error.status_code == 404

    def test_with_resource_details(self) -> None:
        """Test NotFoundError with resource details."""
        response: Dict[str, str] = {"resource": "invoice", "id": "inv_123"}
        error = NotFoundError("Not found", status_code=404, response=response)
        assert error.response == response


class TestServerError:
    """Test cases for ServerError."""

    def test_inheritance(self) -> None:
        """Test that ServerError inherits from NodelaError."""
        error = ServerError("Internal server error")
        assert isinstance(error, NodelaError)
        assert isinstance(error, ServerError)

    def test_with_various_5xx_status_codes(self) -> None:
        """Test ServerError with various 5xx status codes."""
        error_500 = ServerError("Internal error", status_code=500)
        assert error_500.status_code == 500

        error_502 = ServerError("Bad gateway", status_code=502)
        assert error_502.status_code == 502

        error_503 = ServerError("Service unavailable", status_code=503)
        assert error_503.status_code == 503

        error_504 = ServerError("Gateway timeout", status_code=504)
        assert error_504.status_code == 504

    def test_with_error_details(self) -> None:
        """Test ServerError with error details."""
        response: Dict[str, str] = {"error_id": "err_xyz789", "timestamp": "2024-01-01T00:00:00Z"}
        error = ServerError("Server error", status_code=500, response=response)
        assert error.response == response


class TestNetworkError:
    """Test cases for NetworkError."""

    def test_inheritance(self) -> None:
        """Test that NetworkError inherits from NodelaError."""
        error = NetworkError("Connection failed")
        assert isinstance(error, NodelaError)
        assert isinstance(error, NetworkError)

    def test_connection_timeout(self) -> None:
        """Test NetworkError for connection timeout scenarios."""
        error = NetworkError("Request timed out")
        assert str(error) == "Request timed out"
        assert error.status_code is None

    def test_connection_refused(self) -> None:
        """Test NetworkError for connection refused scenarios."""
        error = NetworkError("Connection error: Connection refused")
        assert "Connection refused" in str(error)

    def test_with_underlying_exception_details(self) -> None:
        """Test NetworkError with underlying exception details."""
        error = NetworkError("Connection error: [Errno 111] Connection refused")
        assert "Connection refused" in str(error)
        assert "[Errno 111]" in str(error)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy and type checking."""

    def test_all_specific_errors_inherit_from_nodela_error(self) -> None:
        """Test that all specific exceptions inherit from NodelaError."""
        exceptions = [
            AuthenticationError("test"),
            ValidationError("test"),
            RateLimitError("test"),
            NotFoundError("test"),
            ServerError("test"),
            NetworkError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, NodelaError)
            assert isinstance(exc, Exception)

    def test_exception_catching_hierarchy(self) -> None:
        """Test that exceptions can be caught by parent class."""
        try:
            raise ValidationError("Test validation error")
        except NodelaError as e:
            assert isinstance(e, ValidationError)
            assert str(e) == "Test validation error"

    def test_specific_exception_catching(self) -> None:
        """Test catching specific exception types."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Invalid token")

        assert "Invalid token" in str(exc_info.value)
        assert exc_info.value.status_code is None

    def test_exception_type_differentiation(self) -> None:
        """Test that different exception types are distinct."""
        auth_error = AuthenticationError("auth")
        validation_error = ValidationError("validation")

        assert type(auth_error) is not type(validation_error)
        assert not isinstance(auth_error, ValidationError)
        assert not isinstance(validation_error, AuthenticationError)
        assert isinstance(auth_error, NodelaError)
        assert isinstance(validation_error, NodelaError)
