"""Unit tests for Invoices resource."""

from typing import Any, Dict
from unittest.mock import patch

import pytest

from nodela.models.invoice import (
    CreateInvoiceParams,
    CreateInvoiceResponse,
    CustomerParams,
    VerifyInvoiceResponse,
)
from nodela.resources.invoices import Invoices
from nodela.utils.http import HTTPClient


class TestInvoicesResourceInitialization:
    """Test cases for Invoices resource initialization."""

    def test_initialization(self, http_client: HTTPClient) -> None:
        """Test Invoices resource initialization."""
        invoices = Invoices(http_client)

        assert invoices._http == http_client
        assert invoices.RESOURCE_PATH == "v1/invoices"

    def test_resource_path_is_correct(self, http_client: HTTPClient) -> None:
        """Test that resource path is correctly set."""
        invoices = Invoices(http_client)

        assert invoices.RESOURCE_PATH == "v1/invoices"


class TestInvoicesCreate:
    """Test cases for creating invoices."""

    def test_create_minimal_invoice(
        self, http_client: HTTPClient, mock_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test creating invoice with minimal parameters."""
        invoices = Invoices(http_client)
        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with patch.object(http_client, "post", return_value=mock_invoice_response_data):
            response = invoices.create(params)

        assert isinstance(response, CreateInvoiceResponse)
        assert response.success is True
        assert response.data is not None
        assert response.data.id == "inv_test123"

    def test_create_full_invoice(
        self, http_client: HTTPClient, mock_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test creating invoice with all parameters."""
        invoices = Invoices(http_client)
        customer = CustomerParams(email="test@example.com", name="Test User")
        params = CreateInvoiceParams(
            amount=250.50,
            currency="EUR",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            webhook_url="https://example.com/webhook",
            reference="ORDER-123",
            customer=customer,
            title="Test Invoice",
            description="Test invoice description",
        )

        with patch.object(http_client, "post", return_value=mock_invoice_response_data):
            response = invoices.create(params)

        assert response.success is True
        assert response.data is not None

    def test_create_accepts_uppercase_currency(
        self, http_client: HTTPClient, mock_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test that uppercase currency is accepted."""
        invoices = Invoices(http_client)
        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with patch.object(
            http_client, "post", return_value=mock_invoice_response_data
        ) as mock_post:
            invoices.create(params)

        # Check that post was called with uppercase currency
        call_args = mock_post.call_args
        payload = call_args[1]["data"]
        assert payload["currency"] == "USD"

    def test_create_lowercase_currency_raises_validation_error(
        self, http_client: HTTPClient
    ) -> None:
        """Test that lowercase currency raises validation error."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError) as exc_info:
            CreateInvoiceParams(amount=100.0, currency="usd")  # type: ignore

        errors = exc_info.value.errors()
        assert any("currency" in str(error["loc"]) for error in errors)

    def test_create_unsupported_currency_raises_validation_error(
        self, http_client: HTTPClient
    ) -> None:
        """Test that unsupported currency raises validation error."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError) as exc_info:
            CreateInvoiceParams(amount=100.0, currency="XYZ")  # type: ignore

        errors = exc_info.value.errors()
        assert any("currency" in str(error["loc"]) for error in errors)

    def test_create_calls_correct_endpoint(
        self, http_client: HTTPClient, mock_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test that create calls the correct API endpoint."""
        invoices = Invoices(http_client)
        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with patch.object(
            http_client, "post", return_value=mock_invoice_response_data
        ) as mock_post:
            invoices.create(params)

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "v1/invoices"

    def test_create_includes_all_params_in_payload(
        self, http_client: HTTPClient, mock_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test that all parameters are included in the payload."""
        invoices = Invoices(http_client)
        customer = CustomerParams(email="test@example.com", name="Test User")
        params = CreateInvoiceParams(
            amount=100.0,
            currency="USD",
            success_url="https://example.com/success",
            reference="REF-001",
            customer=customer,
            title="Invoice",
        )

        with patch.object(
            http_client, "post", return_value=mock_invoice_response_data
        ) as mock_post:
            invoices.create(params)

        call_args = mock_post.call_args
        payload = call_args[1]["data"]
        assert payload["amount"] == 100.0
        assert payload["currency"] == "USD"
        assert payload["success_url"] == "https://example.com/success"
        assert payload["reference"] == "REF-001"
        assert payload["title"] == "Invoice"
        assert "customer" in payload

    def test_create_returns_error_response(
        self, http_client: HTTPClient, mock_error_response_data: Dict[str, Any]
    ) -> None:
        """Test handling error response from create."""
        invoices = Invoices(http_client)
        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with patch.object(http_client, "post", return_value=mock_error_response_data):
            response = invoices.create(params)

        assert response.success is False
        assert response.error is not None
        assert response.error.code == "validation_error"
        assert response.data is None

    def test_create_with_different_currencies(
        self, http_client: HTTPClient, mock_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test creating invoices with various supported currencies."""
        invoices = Invoices(http_client)
        currencies = ["USD", "EUR", "GBP", "JPY", "NGN", "AUD"]

        for currency in currencies:
            params = CreateInvoiceParams(amount=100.0, currency=currency)

            with patch.object(http_client, "post", return_value=mock_invoice_response_data):
                response = invoices.create(params)

            assert response.success is True


class TestInvoicesVerify:
    """Test cases for verifying invoices."""

    def test_verify_invoice(
        self, http_client: HTTPClient, mock_verify_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test verifying an invoice."""
        invoices = Invoices(http_client)
        invoice_id = "inv_test123"

        with patch.object(http_client, "get", return_value=mock_verify_invoice_response_data):
            response = invoices.verify(invoice_id)

        assert isinstance(response, VerifyInvoiceResponse)
        assert response.success is True
        assert response.data is not None
        assert response.data.id == "inv_test123"

    def test_verify_calls_correct_endpoint(
        self, http_client: HTTPClient, mock_verify_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test that verify calls the correct API endpoint."""
        invoices = Invoices(http_client)
        invoice_id = "inv_test123"

        with patch.object(
            http_client, "get", return_value=mock_verify_invoice_response_data
        ) as mock_get:
            invoices.verify(invoice_id)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        # Should call v1/invoices/{invoice_id}/verify
        assert call_args[0][0] == "v1/invoices/inv_test123/verify"

    def test_verify_paid_invoice(
        self, http_client: HTTPClient, mock_verify_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test verifying a paid invoice."""
        invoices = Invoices(http_client)
        invoice_id = "inv_test123"

        with patch.object(http_client, "get", return_value=mock_verify_invoice_response_data):
            response = invoices.verify(invoice_id)

        assert response.data is not None
        assert response.data.paid is True
        assert response.data.status == "completed"
        assert response.data.payment is not None

    def test_verify_unpaid_invoice(self, http_client: HTTPClient) -> None:
        """Test verifying an unpaid invoice."""
        unpaid_response: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_test123",
                "invoice_id": "INV-2024-001",
                "original_amount": "100.00",
                "original_currency": "USD",
                "amount": 100.0,
                "currency": "USDC",
                "status": "pending",
                "paid": False,
                "created_at": "2024-01-01T00:00:00Z",
            },
        }

        invoices = Invoices(http_client)
        invoice_id = "inv_test123"

        with patch.object(http_client, "get", return_value=unpaid_response):
            response = invoices.verify(invoice_id)

        assert response.data is not None
        assert response.data.paid is False
        assert response.data.payment is None

    def test_verify_error_response(
        self, http_client: HTTPClient, mock_error_response_data: Dict[str, Any]
    ) -> None:
        """Test handling error response from verify."""
        invoices = Invoices(http_client)
        invoice_id = "inv_nonexistent"

        with patch.object(http_client, "get", return_value=mock_error_response_data):
            response = invoices.verify(invoice_id)

        assert response.success is False
        assert response.error is not None
        assert response.data is None

    def test_verify_with_different_invoice_ids(
        self, http_client: HTTPClient, mock_verify_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test verifying invoices with different ID formats."""
        invoices = Invoices(http_client)
        invoice_ids = ["inv_test123", "inv_abc456", "invoice_12345", "INV-2024-001"]

        for invoice_id in invoice_ids:
            with patch.object(http_client, "get", return_value=mock_verify_invoice_response_data):
                response = invoices.verify(invoice_id)

            assert response.success is True


class TestInvoicesBuildEndpoint:
    """Test cases for endpoint building."""

    def test_build_endpoint(self, http_client: HTTPClient) -> None:
        """Test _build_endpoint method."""
        invoices = Invoices(http_client)

        endpoint = invoices._build_endpoint("v1/invoices", "inv_123", "verify")

        assert endpoint == "v1/invoices/inv_123/verify"

    def test_build_endpoint_single_part(self, http_client: HTTPClient) -> None:
        """Test building endpoint with single part."""
        invoices = Invoices(http_client)

        endpoint = invoices._build_endpoint("v1/invoices")

        assert endpoint == "v1/invoices"

    def test_build_endpoint_with_integers(self, http_client: HTTPClient) -> None:
        """Test building endpoint with integer parts."""
        invoices = Invoices(http_client)

        endpoint = invoices._build_endpoint("v1/invoices", 123, "verify")

        assert endpoint == "v1/invoices/123/verify"


class TestInvoicesIntegration:
    """Integration-style tests for Invoices resource."""

    def test_create_and_verify_flow(
        self,
        http_client: HTTPClient,
        mock_invoice_response_data: Dict[str, Any],
        mock_verify_invoice_response_data: Dict[str, Any],
    ) -> None:
        """Test the flow of creating and then verifying an invoice."""
        invoices = Invoices(http_client)

        # Create invoice
        params = CreateInvoiceParams(amount=100.0, currency="USD", reference="ORDER-001")

        with patch.object(http_client, "post", return_value=mock_invoice_response_data):
            create_response = invoices.create(params)

        assert create_response.success is True
        assert create_response.data is not None
        invoice_id = create_response.data.id

        # Verify invoice
        with patch.object(http_client, "get", return_value=mock_verify_invoice_response_data):
            verify_response = invoices.verify(invoice_id)

        assert verify_response.success is True
        assert verify_response.data is not None
        assert verify_response.data.id == invoice_id

    def test_create_with_customer_info(
        self, http_client: HTTPClient, mock_invoice_response_data: Dict[str, Any]
    ) -> None:
        """Test creating invoice with customer information."""
        invoices = Invoices(http_client)
        customer = CustomerParams(email="customer@example.com", name="John Doe")
        params = CreateInvoiceParams(
            amount=150.0,
            currency="EUR",
            customer=customer,
            title="Premium Subscription",
            description="Monthly premium plan",
        )

        with patch.object(
            http_client, "post", return_value=mock_invoice_response_data
        ) as mock_post:
            response = invoices.create(params)

        assert response.success is True

        # Verify customer info was sent
        call_args = mock_post.call_args
        payload = call_args[1]["data"]
        assert "customer" in payload
        assert payload["customer"]["email"] == "customer@example.com"
        assert payload["customer"]["name"] == "John Doe"
