"""Transaction resource for listing transactions."""

from typing import Optional

from ..models.transaction import ListTransactionsResponse
from .base import BaseResource


class Transactions(BaseResource):
    """Resource for managing transactions."""

    RESOURCE_PATH = "v1/transactions"

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> ListTransactionsResponse:
        """
        List transactions with optional pagination.

        Args:
            page: Page number for pagination.
            limit: Number of results per page.

        Returns:
            ListTransactionsResponse with transactions and pagination info.
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        data = self._http.get(self.RESOURCE_PATH, params=params or None)
        return ListTransactionsResponse.from_dict(data)
