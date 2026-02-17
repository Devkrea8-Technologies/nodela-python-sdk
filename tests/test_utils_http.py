"""Unit tests for HTTP client utilities."""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from nodela.exceptions import (
    AuthenticationError,
    NetworkError,
    NodelaError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from nodela.utils.http import HTTPClient


class TestHTTPClientInitialization:
    """Test cases for HTTPClient initialization."""

    def test_basic_initialization(self, api_key: str, base_url: str) -> None:
        """Test basic HTTPClient initialization."""
        client = HTTPClient(base_url=base_url, api_key=api_key, timeout=30, max_retries=3)

        assert client.base_url == base_url
        assert client.api_key == api_key
        assert client.timeout == 30
        assert client.session is not None

    def test_initialization_strips_trailing_slash(self, api_key: str) -> None:
        """Test that trailing slash is stripped from base URL."""
        client = HTTPClient(base_url="https://api.nodela.co/", api_key=api_key)

        assert client.base_url == "https://api.nodela.co"
        assert not client.base_url.endswith("/")

    def test_initialization_with_custom_timeout(self, api_key: str, base_url: str) -> None:
        """Test initialization with custom timeout."""
        client = HTTPClient(base_url=base_url, api_key=api_key, timeout=60)

        assert client.timeout == 60

    def test_initialization_with_custom_retries(self, api_key: str, base_url: str) -> None:
        """Test initialization with custom max retries."""
        client = HTTPClient(base_url=base_url, api_key=api_key, max_retries=5)

        # Session should be configured
        assert client.session is not None

    def test_session_has_retry_adapter(self, http_client: HTTPClient) -> None:
        """Test that session has retry adapter mounted."""
        assert "https://" in http_client.session.adapters
        assert "http://" in http_client.session.adapters


class TestHTTPClientHeaders:
    """Test cases for HTTPClient header building."""

    def test_get_headers_basic(self, http_client: HTTPClient) -> None:
        """Test basic header generation."""
        headers = http_client._get_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {http_client.api_key}"
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "NodelaSDK/1.0"

    def test_get_headers_with_custom_headers(self, http_client: HTTPClient) -> None:
        """Test header generation with custom headers."""
        custom = {"X-Custom-Header": "custom-value"}
        headers = http_client._get_headers(custom)

        assert headers["Authorization"] == f"Bearer {http_client.api_key}"
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Custom-Header"] == "custom-value"

    def test_get_headers_custom_overrides_default(self, http_client: HTTPClient) -> None:
        """Test that custom headers can override defaults."""
        custom = {"Content-Type": "application/xml"}
        headers = http_client._get_headers(custom)

        assert headers["Content-Type"] == "application/xml"

    def test_get_headers_preserves_auth(self, http_client: HTTPClient) -> None:
        """Test that authorization header is always present."""
        custom = {"Authorization": "Bearer different_token"}
        headers = http_client._get_headers(custom)

        # Custom auth should override
        assert headers["Authorization"] == "Bearer different_token"


class TestHTTPClientResponseHandling:
    """Test cases for HTTPClient response handling."""

    def test_handle_response_success_200(self, http_client: HTTPClient) -> None:
        """Test handling successful 200 response."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}

        result = http_client._handle_response(mock_response)

        assert result == {"data": "success"}

    def test_handle_response_success_201(self, http_client: HTTPClient) -> None:
        """Test handling successful 201 response."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": "created"}

        result = http_client._handle_response(mock_response)

        assert result == {"data": "created"}

    def test_handle_response_invalid_json(self, http_client: HTTPClient) -> None:
        """Test handling response with invalid JSON."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Plain text response"

        result = http_client._handle_response(mock_response)

        assert result == {"message": "Plain text response"}

    def test_handle_response_401_raises_auth_error(self, http_client: HTTPClient) -> None:
        """Test that 401 response raises AuthenticationError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Unauthorized"}

        with pytest.raises(AuthenticationError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)

    def test_handle_response_400_raises_validation_error(self, http_client: HTTPClient) -> None:
        """Test that 400 response raises ValidationError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request"}

        with pytest.raises(ValidationError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 400

    def test_handle_response_422_raises_validation_error(self, http_client: HTTPClient) -> None:
        """Test that 422 response raises ValidationError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Unprocessable entity"}

        with pytest.raises(ValidationError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 422

    def test_handle_response_404_raises_not_found_error(self, http_client: HTTPClient) -> None:
        """Test that 404 response raises NotFoundError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}

        with pytest.raises(NotFoundError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 404

    def test_handle_response_429_raises_rate_limit_error(self, http_client: HTTPClient) -> None:
        """Test that 429 response raises RateLimitError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Too many requests"}

        with pytest.raises(RateLimitError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 429

    def test_handle_response_500_raises_server_error(self, http_client: HTTPClient) -> None:
        """Test that 500 response raises ServerError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}

        with pytest.raises(ServerError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 500

    def test_handle_response_502_raises_server_error(self, http_client: HTTPClient) -> None:
        """Test that 502 response raises ServerError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 502
        mock_response.json.return_value = {"message": "Bad gateway"}

        with pytest.raises(ServerError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 502

    def test_handle_response_other_status_raises_nodela_error(
        self, http_client: HTTPClient
    ) -> None:
        """Test that other status codes raise NodelaError."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 418  # I'm a teapot
        mock_response.json.return_value = {"message": "I'm a teapot"}

        with pytest.raises(NodelaError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.status_code == 418

    def test_handle_response_includes_response_data(self, http_client: HTTPClient) -> None:
        """Test that exceptions include response data."""
        response_data = {"message": "Error", "details": {"field": "value"}}
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 400
        mock_response.json.return_value = response_data

        with pytest.raises(ValidationError) as exc_info:
            http_client._handle_response(mock_response)

        assert exc_info.value.response == response_data


class TestHTTPClientRequest:
    """Test cases for HTTPClient request method."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_get(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test GET request."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_request.return_value = mock_response

        result = http_client.request("GET", "/test-endpoint")

        assert result == {"data": "success"}
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.nodela.co/test-endpoint"

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_post_with_data(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test POST request with data."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": "created"}
        mock_request.return_value = mock_response

        data: Dict[str, Any] = {"key": "value"}
        result = http_client.request("POST", "/create", data=data)

        assert result == {"data": "created"}
        call_args = mock_request.call_args
        assert call_args[1]["json"] == data

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_with_params(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test request with query parameters."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_request.return_value = mock_response

        params: Dict[str, Any] = {"page": 1, "limit": 10}
        http_client.request("GET", "/list", params=params)

        call_args = mock_request.call_args
        assert call_args[1]["params"] == params

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_strips_leading_slash(
        self, mock_request: Mock, http_client: HTTPClient
    ) -> None:
        """Test that leading slash is handled correctly."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_request.return_value = mock_response

        http_client.request("GET", "/endpoint")

        call_args = mock_request.call_args
        assert call_args[1]["url"] == "https://api.nodela.co/endpoint"

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_timeout_raises_network_error(
        self, mock_request: Mock, http_client: HTTPClient
    ) -> None:
        """Test that timeout raises NetworkError."""
        mock_request.side_effect = Timeout("Request timed out")

        with pytest.raises(NetworkError) as exc_info:
            http_client.request("GET", "/slow-endpoint")

        assert "timed out" in str(exc_info.value)

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_connection_error_raises_network_error(
        self, mock_request: Mock, http_client: HTTPClient
    ) -> None:
        """Test that connection error raises NetworkError."""
        mock_request.side_effect = ConnectionError("Connection refused")

        with pytest.raises(NetworkError) as exc_info:
            http_client.request("GET", "/endpoint")

        assert "Connection error" in str(exc_info.value)

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_generic_exception_raises_nodela_error(
        self, mock_request: Mock, http_client: HTTPClient
    ) -> None:
        """Test that generic RequestException raises NodelaError."""
        mock_request.side_effect = RequestException("Generic error")

        with pytest.raises(NodelaError) as exc_info:
            http_client.request("GET", "/endpoint")

        assert "Request failed" in str(exc_info.value)

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_includes_headers(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test that request includes proper headers."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_request.return_value = mock_response

        http_client.request("GET", "/endpoint")

        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert "User-Agent" in headers

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_with_custom_headers(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test request with custom headers."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_request.return_value = mock_response

        custom_headers = {"X-Custom": "value"}
        http_client.request("GET", "/endpoint", headers=custom_headers)

        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert headers["X-Custom"] == "value"


class TestHTTPClientConvenienceMethods:
    """Test cases for HTTPClient convenience methods."""

    @patch("nodela.utils.http.HTTPClient.request")
    def test_get_method(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test GET convenience method."""
        mock_request.return_value = {"data": "success"}

        result = http_client.get("/endpoint")

        assert result == {"data": "success"}
        mock_request.assert_called_once_with("GET", "/endpoint", params=None)

    @patch("nodela.utils.http.HTTPClient.request")
    def test_get_method_with_params(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test GET method with params."""
        mock_request.return_value = {"data": "success"}
        params: Dict[str, int] = {"page": 1}

        http_client.get("/endpoint", params=params)

        mock_request.assert_called_once_with("GET", "/endpoint", params=params)

    @patch("nodela.utils.http.HTTPClient.request")
    def test_post_method(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test POST convenience method."""
        mock_request.return_value = {"data": "created"}

        result = http_client.post("/endpoint")

        assert result == {"data": "created"}
        mock_request.assert_called_once_with("POST", "/endpoint", data=None)

    @patch("nodela.utils.http.HTTPClient.request")
    def test_post_method_with_data(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test POST method with data."""
        mock_request.return_value = {"data": "created"}
        data: Dict[str, str] = {"key": "value"}

        http_client.post("/endpoint", data=data)

        mock_request.assert_called_once_with("POST", "/endpoint", data=data)

    @patch("nodela.utils.http.HTTPClient.request")
    def test_put_method(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test PUT convenience method."""
        mock_request.return_value = {"data": "updated"}
        data: Dict[str, str] = {"key": "value"}

        result = http_client.put("/endpoint", data=data)

        assert result == {"data": "updated"}
        mock_request.assert_called_once_with("PUT", "/endpoint", data=data)

    @patch("nodela.utils.http.HTTPClient.request")
    def test_patch_method(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test PATCH convenience method."""
        mock_request.return_value = {"data": "patched"}
        data: Dict[str, str] = {"key": "value"}

        result = http_client.patch("/endpoint", data=data)

        assert result == {"data": "patched"}
        mock_request.assert_called_once_with("PATCH", "/endpoint", data=data)

    @patch("nodela.utils.http.HTTPClient.request")
    def test_delete_method(self, mock_request: Mock, http_client: HTTPClient) -> None:
        """Test DELETE convenience method."""
        mock_request.return_value = {"data": "deleted"}

        result = http_client.delete("/endpoint")

        assert result == {"data": "deleted"}
        mock_request.assert_called_once_with("DELETE", "/endpoint")
