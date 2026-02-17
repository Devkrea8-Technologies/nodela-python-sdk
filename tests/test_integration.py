"""Integration tests for the Nodela SDK."""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
import requests

from nodela import NodelaClient
from nodela.exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from nodela.models.invoice import CreateInvoiceParams, CustomerParams


class TestEndToEndInvoiceFlow:
    """End-to-end tests for invoice operations."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_create_and_verify_invoice_success(self, mock_request: Mock, api_key: str) -> None:
        """Test complete flow of creating and verifying an invoice."""
        # Setup client
        client = NodelaClient(api_key=api_key)

        # Mock create invoice response
        create_response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_integration_test",
                "invoice_id": "INV-2024-001",
                "original_amount": "100.00",
                "original_currency": "USD",
                "amount": "100.00",
                "currency": "USDC",
                "checkout_url": "https://checkout.nodela.co/inv_integration_test",
                "created_at": "2024-01-01T00:00:00Z",
            },
        }

        create_mock_response = Mock(spec=requests.Response)
        create_mock_response.status_code = 201
        create_mock_response.json.return_value = create_response_data

        # Mock verify invoice response
        verify_response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_integration_test",
                "invoice_id": "INV-2024-001",
                "original_amount": "100.00",
                "original_currency": "USD",
                "amount": 100.0,
                "currency": "USDC",
                "status": "completed",
                "paid": True,
                "created_at": "2024-01-01T00:00:00Z",
                "payment": {
                    "id": "pay_integration_test",
                    "network": "polygon",
                    "token": "USDC",
                    "address": "0x1234567890abcdef",
                    "amount": 100.0,
                    "status": "confirmed",
                    "tx_hash": ["0xabcdef1234567890"],
                    "transaction_type": "payment",
                    "payer_email": "payer@example.com",
                    "created_at": "2024-01-01T00:05:00Z",
                },
            },
        }

        verify_mock_response = Mock(spec=requests.Response)
        verify_mock_response.status_code = 200
        verify_mock_response.json.return_value = verify_response_data

        # Configure mock to return different responses for create and verify
        mock_request.side_effect = [create_mock_response, verify_mock_response]

        # Create invoice
        params = CreateInvoiceParams(
            amount=100.0, currency="USD", reference="ORDER-INTEGRATION-001"
        )
        create_response = client.invoices.create(params)

        assert create_response.success is True
        assert create_response.data is not None
        assert create_response.data.id == "inv_integration_test"
        invoice_id = create_response.data.id

        # Verify invoice
        verify_response = client.invoices.verify(invoice_id)

        assert verify_response.success is True
        assert verify_response.data is not None
        assert verify_response.data.paid is True
        assert verify_response.data.payment is not None

    @patch("nodela.utils.http.requests.Session.request")
    def test_create_invoice_with_customer_info(self, mock_request: Mock, api_key: str) -> None:
        """Test creating invoice with customer information."""
        client = NodelaClient(api_key=api_key)

        response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_test",
                "invoice_id": "INV-001",
                "original_amount": "250.00",
                "original_currency": "EUR",
                "amount": "250.00",
                "currency": "USDC",
                "customer": {"email": "customer@example.com", "name": "John Doe"},
                "checkout_url": "https://checkout.nodela.co/inv_test",
                "created_at": "2024-01-01T00:00:00Z",
            },
        }

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        customer = CustomerParams(email="customer@example.com", name="John Doe")
        params = CreateInvoiceParams(
            amount=250.0,
            currency="EUR",
            customer=customer,
            title="Premium Service",
            description="Monthly subscription",
        )

        response = client.invoices.create(params)

        assert response.success is True
        assert response.data is not None
        assert response.data.customer is not None
        assert response.data.customer.email == "customer@example.com"
        assert response.data.customer.name == "John Doe"


class TestEndToEndTransactionFlow:
    """End-to-end tests for transaction operations."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_list_transactions_pagination(self, mock_request: Mock, api_key: str) -> None:
        """Test listing transactions with pagination."""
        client = NodelaClient(api_key=api_key)

        # First page
        page1_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "transactions": [
                    {
                        "id": f"txn_{i}",
                        "invoice_id": f"INV-{i}",
                        "reference": f"ORDER-{i}",
                        "original_amount": 100.0,
                        "original_currency": "USD",
                        "amount": 100.0,
                        "currency": "USDC",
                        "exchange_rate": 1.0,
                        "title": f"Transaction {i}",
                        "description": "Description",
                        "status": "completed",
                        "paid": True,
                        "customer": {"email": f"user{i}@example.com", "name": f"User {i}"},
                        "created_at": "2024-01-01T00:00:00Z",
                        "payment": {
                            "id": f"pay_{i}",
                            "network": "polygon",
                            "token": "USDC",
                            "address": "0x1234",
                            "amount": 100.0,
                            "status": "confirmed",
                            "tx_hash": [f"0xhash{i}"],
                            "transaction_type": "payment",
                            "payer_email": f"payer{i}@example.com",
                            "created_at": "2024-01-01T00:05:00Z",
                        },
                    }
                    for i in range(1, 11)
                ],
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": 25,
                    "total_pages": 3,
                    "has_more": True,
                },
            },
        }

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = page1_data
        mock_request.return_value = mock_response

        response = client.transactions.list(page=1, limit=10)

        assert response.success is True
        assert len(response.data.transactions) == 10
        assert response.data.pagination.has_more is True
        assert response.data.pagination.total == 25


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_authentication_error_handling(self, mock_request: Mock, api_key: str) -> None:
        """Test handling of authentication errors."""
        client = NodelaClient(api_key=api_key)

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_request.return_value = mock_response

        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with pytest.raises(AuthenticationError) as exc_info:
            client.invoices.create(params)

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)

    @patch("nodela.utils.http.requests.Session.request")
    def test_validation_error_handling(self, mock_request: Mock, api_key: str) -> None:
        """Test handling of validation errors."""
        client = NodelaClient(api_key=api_key)

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Invalid amount"}
        mock_request.return_value = mock_response

        params = CreateInvoiceParams(amount=-100.0, currency="USD")

        with pytest.raises(ValidationError) as exc_info:
            client.invoices.create(params)

        assert exc_info.value.status_code == 422

    @patch("nodela.utils.http.requests.Session.request")
    def test_not_found_error_handling(self, mock_request: Mock, api_key: str) -> None:
        """Test handling of not found errors."""
        client = NodelaClient(api_key=api_key)

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Invoice not found"}
        mock_request.return_value = mock_response

        with pytest.raises(NotFoundError) as exc_info:
            client.invoices.verify("inv_nonexistent")

        assert exc_info.value.status_code == 404

    @patch("nodela.utils.http.requests.Session.request")
    def test_rate_limit_error_handling(self, mock_request: Mock, api_key: str) -> None:
        """Test handling of rate limit errors."""
        client = NodelaClient(api_key=api_key)

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Too many requests"}
        mock_request.return_value = mock_response

        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with pytest.raises(RateLimitError) as exc_info:
            client.invoices.create(params)

        assert exc_info.value.status_code == 429

    @patch("nodela.utils.http.requests.Session.request")
    def test_server_error_handling(self, mock_request: Mock, api_key: str) -> None:
        """Test handling of server errors."""
        client = NodelaClient(api_key=api_key)

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_request.return_value = mock_response

        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with pytest.raises(ServerError) as exc_info:
            client.invoices.create(params)

        assert exc_info.value.status_code == 500

    @patch("nodela.utils.http.requests.Session.request")
    def test_network_error_handling(self, mock_request: Mock, api_key: str) -> None:
        """Test handling of network errors."""
        client = NodelaClient(api_key=api_key)

        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

        params = CreateInvoiceParams(amount=100.0, currency="USD")

        with pytest.raises(NetworkError) as exc_info:
            client.invoices.create(params)

        assert "timed out" in str(exc_info.value)


class TestMultiCurrencySupport:
    """Integration tests for multi-currency support."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_various_supported_currencies(self, mock_request: Mock, api_key: str) -> None:
        """Test creating invoices with various supported currencies."""
        client = NodelaClient(api_key=api_key)

        currencies = [
            ("USD", 100.0),
            ("EUR", 85.0),
            ("GBP", 75.0),
            ("NGN", 75000.0),
            ("JPY", 11000.0),
        ]

        for currency, amount in currencies:
            response_data: Dict[str, Any] = {
                "success": True,
                "data": {
                    "id": f"inv_{currency.lower()}",
                    "invoice_id": f"INV-{currency}",
                    "original_amount": str(amount),
                    "original_currency": currency,
                    "amount": str(amount),
                    "currency": "USDC",
                    "checkout_url": f"https://checkout.nodela.co/inv_{currency.lower()}",
                    "created_at": "2024-01-01T00:00:00Z",
                },
            }

            mock_response = Mock(spec=requests.Response)
            mock_response.status_code = 201
            mock_response.json.return_value = response_data
            mock_request.return_value = mock_response

            params = CreateInvoiceParams(amount=amount, currency=currency)
            response = client.invoices.create(params)

            assert response.success is True
            assert response.data is not None
            assert response.data.original_currency == currency

    def test_unsupported_currency_raises_validation_error(self, api_key: str) -> None:
        """Test that unsupported currency raises validation error."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError) as exc_info:
            CreateInvoiceParams(amount=100.0, currency="INVALID")  # type: ignore

        errors = exc_info.value.errors()
        assert any("currency" in str(error["loc"]) for error in errors)


class TestClientConfiguration:
    """Integration tests for client configuration."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_custom_timeout_respected(self, mock_request: Mock, api_key: str) -> None:
        """Test that custom timeout is respected."""
        client = NodelaClient(api_key=api_key, timeout=5)

        response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "transactions": [],
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": 0,
                    "total_pages": 0,
                    "has_more": False,
                },
            },
        }

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        client.transactions.list()

        # Verify timeout was passed to request
        call_args = mock_request.call_args
        assert call_args[1]["timeout"] == 5

    def test_multiple_clients_independent(self, api_key: str) -> None:
        """Test that multiple clients operate independently."""
        client1 = NodelaClient(api_key=api_key, timeout=30)
        client2 = NodelaClient(api_key=api_key, timeout=60)

        assert client1._http.timeout == 30
        assert client2._http.timeout == 60
        assert client1._http is not client2._http


class TestHeadersAndAuthentication:
    """Integration tests for headers and authentication."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_authorization_header_included(self, mock_request: Mock, api_key: str) -> None:
        """Test that authorization header is included in requests."""
        client = NodelaClient(api_key=api_key)

        response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "transactions": [],
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": 0,
                    "total_pages": 0,
                    "has_more": False,
                },
            },
        }

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        client.transactions.list()

        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {api_key}"

    @patch("nodela.utils.http.requests.Session.request")
    def test_user_agent_header_included(self, mock_request: Mock, api_key: str) -> None:
        """Test that user agent header is included."""
        client = NodelaClient(api_key=api_key)

        response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "transactions": [],
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": 0,
                    "total_pages": 0,
                    "has_more": False,
                },
            },
        }

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        client.transactions.list()

        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert "User-Agent" in headers
        assert headers["User-Agent"] == "NodelaSDK/1.0"


class TestDataSerialization:
    """Integration tests for data serialization."""

    @patch("nodela.utils.http.requests.Session.request")
    def test_request_data_properly_serialized(self, mock_request: Mock, api_key: str) -> None:
        """Test that request data is properly serialized to JSON."""
        client = NodelaClient(api_key=api_key)

        response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_test",
                "invoice_id": "INV-001",
                "original_amount": "100.00",
                "original_currency": "USD",
                "amount": "100.00",
                "currency": "USDC",
                "checkout_url": "https://checkout.nodela.co/inv_test",
                "created_at": "2024-01-01T00:00:00Z",
            },
        }

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        params = CreateInvoiceParams(amount=100.0, currency="USD", reference="ORDER-001")

        client.invoices.create(params)

        call_args = mock_request.call_args
        json_data = call_args[1]["json"]
        assert json_data["amount"] == 100.0
        assert json_data["currency"] == "USD"
        assert json_data["reference"] == "ORDER-001"

    @patch("nodela.utils.http.requests.Session.request")
    def test_response_data_properly_deserialized(self, mock_request: Mock, api_key: str) -> None:
        """Test that response data is properly deserialized from JSON."""
        client = NodelaClient(api_key=api_key)

        response_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_test",
                "invoice_id": "INV-001",
                "original_amount": "100.00",
                "original_currency": "USD",
                "amount": "100.00",
                "currency": "USDC",
                "checkout_url": "https://checkout.nodela.co/inv_test",
                "created_at": "2024-01-01T00:00:00Z",
            },
        }

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        params = CreateInvoiceParams(amount=100.0, currency="USD")
        response = client.invoices.create(params)

        assert response.success is True
        assert response.data is not None
        assert response.data.id == "inv_test"
        assert response.data.original_currency == "USD"
