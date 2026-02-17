"""Invoice resource for creating and verifying invoices."""

from ..models.invoice import (
    SUPPORTED_CURRENCIES,
    CreateInvoiceParams,
    CreateInvoiceResponse,
    VerifyInvoiceResponse,
)
from .base import BaseResource


class Invoices(BaseResource):
    """Resource for managing invoices."""

    RESOURCE_PATH = "v1/invoices"

    def create(self, params: CreateInvoiceParams) -> CreateInvoiceResponse:
        """
        Create a new invoice.

        Args:
            params: Invoice creation parameters.

        Returns:
            CreateInvoiceResponse with invoice data and checkout URL.

        Raises:
            ValueError: If the currency is not supported.
        """
        upper = params.currency.upper()
        if upper not in SUPPORTED_CURRENCIES:
            raise ValueError(
                f'Unsupported currency: "{params.currency}". '
                f"Supported currencies: {', '.join(SUPPORTED_CURRENCIES)}"
            )

        payload = params.to_dict()
        payload["currency"] = upper

        data = self._http.post(self.RESOURCE_PATH, data=payload)
        return CreateInvoiceResponse.from_dict(data)

    def verify(self, invoice_id: str) -> VerifyInvoiceResponse:
        """
        Verify an invoice's payment status.

        Args:
            invoice_id: The ID of the invoice to verify.

        Returns:
            VerifyInvoiceResponse with invoice and payment details.
        """
        endpoint = self._build_endpoint(self.RESOURCE_PATH, invoice_id, "verify")
        data = self._http.get(endpoint)
        return VerifyInvoiceResponse.from_dict(data)
