"""Base resource class for API endpoints."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.http import HTTPClient


class BaseResource:
    """Base class for API resources"""

    def __init__(self, http_client: "HTTPClient") -> None:
        self._http = http_client

    def _build_endpoint(self, *parts: str) -> str:
        """Build endpoint URL from parts."""
        return "/".join(str(part) for part in parts)
