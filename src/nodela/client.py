"""Main SDK client."""

import os
from typing import Optional

from .exceptions import AuthenticationError
from .resources.invoices import Invoices
from .resources.transactions import Transactions
from .utils.http import HTTPClient


class NodelaClient:
    """
    Main client for interacting with Nodela.

    Args:
      api_key: Your API key. If not provided, will look for NODELA_API_KEY env var
      timeout: Reuqest timeout in seconds. Defaults to 30.
      max_retries: Maximum number of retires for failed requests. Defaults to 3

    Example
    ```python
      from nodela import NodelaClient

      client = NodelaClient(api_key="your_api_key")
    ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key or os.getenv("NODELA_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass it as api_key parameter or "
                "set NODELA_API_KEY environment variable"
            )

        self._http = HTTPClient(
            base_url="https://api.nodela.co",
            api_key=self.api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Resources
        self.invoices = Invoices(self._http)
        self.transactions = Transactions(self._http)
