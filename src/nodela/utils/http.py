"""HTTP utilities for API requests."""

from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import (
    AuthenticationError,
    NetworkError,
    NodelaError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class HTTPClient:
    """HTTP client with retry logic and error handling."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "NodelaSDK/1.0",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        try:
            data = response.json()
        except ValueError:
            data = {"message": response.text}

        if response.status_code == 200 or response.status_code == 201:
            return data

        error_message = data.get("message", "An error occurred")

        if response.status_code == 401:
            raise AuthenticationError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code == 400 or response.status_code == 422:
            raise ValidationError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code == 429:
            raise RateLimitError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code >= 500:
            raise ServerError(
                error_message,
                status_code=response.status_code,
                response=data,
            )
        else:
            raise NodelaError(
                error_message,
                status_code=response.status_code,
                response=data,
            )

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NodelaError(f"Request failed: {str(e)}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request."""
        return self.request("POST", endpoint, data=data)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a PUT request."""
        return self.request("PUT", endpoint, data=data)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a PATCH request."""
        return self.request("PATCH", endpoint, data=data)

    def delete(
        self,
        endpoint: str,
    ) -> Any:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint)
