"""Unit tests for invoice models."""

from typing import Any, Dict, List

import pytest
from pydantic import ValidationError as PydanticValidationError

from nodela.models.invoice import (
    SUPPORTED_CURRENCIES,
    CreateInvoiceData,
    CreateInvoiceParams,
    CreateInvoiceResponse,
    CustomerInfo,
    CustomerParams,
    ErrorDetail,
    PaymentInfo,
    VerifyInvoiceData,
    VerifyInvoiceResponse,
)


class TestSupportedCurrencies:
    """Test cases for supported currencies constants."""

    def test_supported_currencies_is_list(self) -> None:
        """Test that SUPPORTED_CURRENCIES is a list."""
        assert isinstance(SUPPORTED_CURRENCIES, list)

    def test_supported_currencies_not_empty(self) -> None:
        """Test that SUPPORTED_CURRENCIES is not empty."""
        assert len(SUPPORTED_CURRENCIES) > 0

    def test_major_currencies_included(self) -> None:
        """Test that major currencies are included."""
        assert "USD" in SUPPORTED_CURRENCIES
        assert "EUR" in SUPPORTED_CURRENCIES
        assert "GBP" in SUPPORTED_CURRENCIES
        assert "JPY" in SUPPORTED_CURRENCIES

    def test_all_currencies_uppercase(self) -> None:
        """Test that all currencies are uppercase."""
        for currency in SUPPORTED_CURRENCIES:
            assert currency == currency.upper()
            assert len(currency) == 3  # ISO 4217 standard

    def test_no_duplicates(self) -> None:
        """Test that there are no duplicate currencies."""
        assert len(SUPPORTED_CURRENCIES) == len(set(SUPPORTED_CURRENCIES))


class TestCustomerParams:
    """Test cases for CustomerParams model."""

    def test_basic_initialization(self) -> None:
        """Test initialization with required email field."""
        customer = CustomerParams(email="test@example.com")
        assert customer.email == "test@example.com"
        assert customer.name is None

    def test_initialization_with_name(self) -> None:
        """Test initialization with name field."""
        customer = CustomerParams(email="test@example.com", name="Test User")
        assert customer.email == "test@example.com"
        assert customer.name == "Test User"

    def test_missing_email_raises_error(self) -> None:
        """Test that missing email raises validation error."""
        with pytest.raises(PydanticValidationError):
            CustomerParams()  # type: ignore

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        customer = CustomerParams(email="test@example.com", name="Test User")
        result = customer.to_dict()
        assert result == {"email": "test@example.com", "name": "Test User"}

    def test_to_dict_without_name(self) -> None:
        """Test to_dict excludes None name."""
        customer = CustomerParams(email="test@example.com")
        result = customer.to_dict()
        assert result == {"email": "test@example.com"}
        assert "name" not in result


class TestCreateInvoiceParams:
    """Test cases for CreateInvoiceParams model."""

    def test_minimal_initialization(self) -> None:
        """Test initialization with only required fields."""
        params = CreateInvoiceParams(amount=100.0, currency="USD")
        assert params.amount == 100.0
        assert params.currency == "USD"
        assert params.success_url is None
        assert params.cancel_url is None
        assert params.webhook_url is None
        assert params.reference is None
        assert params.customer is None
        assert params.title is None
        assert params.description is None

    def test_full_initialization(self) -> None:
        """Test initialization with all fields."""
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

        assert params.amount == 250.50
        assert params.currency == "EUR"
        assert params.success_url == "https://example.com/success"
        assert params.cancel_url == "https://example.com/cancel"
        assert params.webhook_url == "https://example.com/webhook"
        assert params.reference == "ORDER-123"
        assert params.customer == customer
        assert params.title == "Test Invoice"
        assert params.description == "Test invoice description"

    def test_missing_amount_raises_error(self) -> None:
        """Test that missing amount raises validation error."""
        with pytest.raises(PydanticValidationError):
            CreateInvoiceParams(currency="USD")  # type: ignore

    def test_missing_currency_raises_error(self) -> None:
        """Test that missing currency raises validation error."""
        with pytest.raises(PydanticValidationError):
            CreateInvoiceParams(amount=100.0)  # type: ignore

    def test_to_dict_minimal(self) -> None:
        """Test to_dict with minimal data."""
        params = CreateInvoiceParams(amount=100.0, currency="USD")
        result = params.to_dict()
        assert result == {"amount": 100.0, "currency": "USD"}

    def test_to_dict_full(self) -> None:
        """Test to_dict with all fields."""
        customer = CustomerParams(email="test@example.com", name="Test User")
        params = CreateInvoiceParams(
            amount=100.0,
            currency="USD",
            success_url="https://example.com/success",
            reference="REF-001",
            customer=customer,
            title="Invoice Title",
        )
        result = params.to_dict()

        assert result["amount"] == 100.0
        assert result["currency"] == "USD"
        assert result["success_url"] == "https://example.com/success"
        assert result["reference"] == "REF-001"
        assert result["customer"] == {"email": "test@example.com", "name": "Test User"}
        assert result["title"] == "Invoice Title"


class TestErrorDetail:
    """Test cases for ErrorDetail model."""

    def test_initialization(self) -> None:
        """Test ErrorDetail initialization."""
        error = ErrorDetail(code="validation_error", message="Invalid input")
        assert error.code == "validation_error"
        assert error.message == "Invalid input"

    def test_to_dict(self) -> None:
        """Test ErrorDetail to_dict."""
        error = ErrorDetail(code="auth_error", message="Unauthorized")
        result = error.to_dict()
        assert result == {"code": "auth_error", "message": "Unauthorized"}


class TestCustomerInfo:
    """Test cases for CustomerInfo model."""

    def test_initialization_with_name(self) -> None:
        """Test CustomerInfo initialization."""
        customer = CustomerInfo(email="test@example.com", name="Test User")
        assert customer.email == "test@example.com"
        assert customer.name == "Test User"

    def test_initialization_without_name(self) -> None:
        """Test CustomerInfo with optional name."""
        customer = CustomerInfo(email="test@example.com")
        assert customer.email == "test@example.com"
        assert customer.name is None


class TestCreateInvoiceData:
    """Test cases for CreateInvoiceData model."""

    def test_minimal_initialization(self) -> None:
        """Test initialization with required fields."""
        data = CreateInvoiceData(
            id="inv_123",
            invoice_id="INV-001",
            original_amount="100.00",
            original_currency="USD",
            amount="100.00",
            currency="USDC",
            checkout_url="https://checkout.nodela.co/inv_123",
            created_at="2024-01-01T00:00:00Z",
        )

        assert data.id == "inv_123"
        assert data.invoice_id == "INV-001"
        assert data.original_amount == "100.00"
        assert data.original_currency == "USD"
        assert data.amount == "100.00"
        assert data.currency == "USDC"
        assert data.checkout_url == "https://checkout.nodela.co/inv_123"
        assert data.created_at == "2024-01-01T00:00:00Z"

    def test_full_initialization(self) -> None:
        """Test initialization with all fields."""
        customer = CustomerInfo(email="test@example.com", name="Test User")
        data = CreateInvoiceData(
            id="inv_123",
            invoice_id="INV-001",
            original_amount="100.00",
            original_currency="USD",
            amount="100.00",
            currency="USDC",
            exchange_rate="1.0",
            webhook_url="https://example.com/webhook",
            customer=customer,
            checkout_url="https://checkout.nodela.co/inv_123",
            status="pending",
            created_at="2024-01-01T00:00:00Z",
        )

        assert data.exchange_rate == "1.0"
        assert data.webhook_url == "https://example.com/webhook"
        assert data.customer == customer
        assert data.status == "pending"

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        dict_data: Dict[str, Any] = {
            "id": "inv_123",
            "invoice_id": "INV-001",
            "original_amount": "100.00",
            "original_currency": "USD",
            "amount": "100.00",
            "currency": "USDC",
            "checkout_url": "https://checkout.nodela.co/inv_123",
            "created_at": "2024-01-01T00:00:00Z",
        }
        data = CreateInvoiceData.from_dict(dict_data)

        assert data.id == "inv_123"
        assert data.invoice_id == "INV-001"


class TestCreateInvoiceResponse:
    """Test cases for CreateInvoiceResponse model."""

    def test_successful_response(self) -> None:
        """Test successful invoice creation response."""
        invoice_data = CreateInvoiceData(
            id="inv_123",
            invoice_id="INV-001",
            original_amount="100.00",
            original_currency="USD",
            amount="100.00",
            currency="USDC",
            checkout_url="https://checkout.nodela.co/inv_123",
            created_at="2024-01-01T00:00:00Z",
        )
        response = CreateInvoiceResponse(success=True, data=invoice_data)

        assert response.success is True
        assert response.data == invoice_data
        assert response.error is None

    def test_error_response(self) -> None:
        """Test error invoice creation response."""
        error = ErrorDetail(code="validation_error", message="Invalid amount")
        response = CreateInvoiceResponse(success=False, error=error)

        assert response.success is False
        assert response.error == error
        assert response.data is None

    def test_from_dict_success(self) -> None:
        """Test creating successful response from dict."""
        dict_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_123",
                "invoice_id": "INV-001",
                "original_amount": "100.00",
                "original_currency": "USD",
                "amount": "100.00",
                "currency": "USDC",
                "checkout_url": "https://checkout.nodela.co/inv_123",
                "created_at": "2024-01-01T00:00:00Z",
            },
        }
        response = CreateInvoiceResponse.from_dict(dict_data)

        assert response.success is True
        assert response.data is not None
        assert response.data.id == "inv_123"

    def test_from_dict_error(self) -> None:
        """Test creating error response from dict."""
        dict_data: Dict[str, Any] = {
            "success": False,
            "error": {"code": "validation_error", "message": "Invalid input"},
        }
        response = CreateInvoiceResponse.from_dict(dict_data)

        assert response.success is False
        assert response.error is not None
        assert response.error.code == "validation_error"


class TestPaymentInfo:
    """Test cases for PaymentInfo model."""

    def test_initialization(self) -> None:
        """Test PaymentInfo initialization."""
        payment = PaymentInfo(
            id="pay_123",
            network="polygon",
            token="USDC",
            address="0x1234567890abcdef",
            amount=100.0,
            status="confirmed",
            tx_hash=["0xabcdef1234567890"],
            transaction_type="payment",
            payer_email="payer@example.com",
            created_at="2024-01-01T00:05:00Z",
        )

        assert payment.id == "pay_123"
        assert payment.network == "polygon"
        assert payment.token == "USDC"
        assert payment.address == "0x1234567890abcdef"
        assert payment.amount == 100.0
        assert payment.status == "confirmed"
        assert payment.tx_hash == ["0xabcdef1234567890"]
        assert payment.transaction_type == "payment"
        assert payment.payer_email == "payer@example.com"
        assert payment.created_at == "2024-01-01T00:05:00Z"

    def test_multiple_tx_hashes(self) -> None:
        """Test PaymentInfo with multiple transaction hashes."""
        tx_hashes: List[str] = ["0xhash1", "0xhash2", "0xhash3"]
        payment = PaymentInfo(
            id="pay_123",
            network="ethereum",
            token="USDT",
            address="0xaddress",
            amount=50.0,
            status="confirmed",
            tx_hash=tx_hashes,
            transaction_type="payment",
            payer_email="test@example.com",
            created_at="2024-01-01T00:00:00Z",
        )

        assert len(payment.tx_hash) == 3
        assert payment.tx_hash == tx_hashes


class TestVerifyInvoiceData:
    """Test cases for VerifyInvoiceData model."""

    def test_initialization_without_payment(self) -> None:
        """Test initialization for unpaid invoice."""
        data = VerifyInvoiceData(
            id="inv_123",
            invoice_id="INV-001",
            original_amount="100.00",
            original_currency="USD",
            amount=100.0,
            currency="USDC",
            status="pending",
            paid=False,
            created_at="2024-01-01T00:00:00Z",
        )

        assert data.id == "inv_123"
        assert data.invoice_id == "INV-001"
        assert data.paid is False
        assert data.payment is None

    def test_initialization_with_payment(self) -> None:
        """Test initialization for paid invoice."""
        customer = CustomerInfo(email="test@example.com", name="Test User")
        payment = PaymentInfo(
            id="pay_123",
            network="polygon",
            token="USDC",
            address="0x1234",
            amount=100.0,
            status="confirmed",
            tx_hash=["0xhash"],
            transaction_type="payment",
            payer_email="payer@example.com",
            created_at="2024-01-01T00:05:00Z",
        )

        data = VerifyInvoiceData(
            id="inv_123",
            invoice_id="INV-001",
            reference="ORDER-001",
            original_amount="100.00",
            original_currency="USD",
            amount=100.0,
            currency="USDC",
            exchange_rate=1.0,
            title="Test Invoice",
            description="Test Description",
            status="completed",
            paid=True,
            customer=customer,
            created_at="2024-01-01T00:00:00Z",
            payment=payment,
        )

        assert data.paid is True
        assert data.payment == payment
        assert data.customer == customer
        assert data.reference == "ORDER-001"
        assert data.title == "Test Invoice"

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        dict_data: Dict[str, Any] = {
            "id": "inv_123",
            "invoice_id": "INV-001",
            "original_amount": "100.00",
            "original_currency": "USD",
            "amount": 100.0,
            "currency": "USDC",
            "status": "pending",
            "paid": False,
            "created_at": "2024-01-01T00:00:00Z",
        }
        data = VerifyInvoiceData.from_dict(dict_data)

        assert data.id == "inv_123"
        assert data.paid is False


class TestVerifyInvoiceResponse:
    """Test cases for VerifyInvoiceResponse model."""

    def test_successful_response(self) -> None:
        """Test successful verification response."""
        invoice_data = VerifyInvoiceData(
            id="inv_123",
            invoice_id="INV-001",
            original_amount="100.00",
            original_currency="USD",
            amount=100.0,
            currency="USDC",
            status="completed",
            paid=True,
            created_at="2024-01-01T00:00:00Z",
        )
        response = VerifyInvoiceResponse(success=True, data=invoice_data)

        assert response.success is True
        assert response.data == invoice_data
        assert response.error is None

    def test_error_response(self) -> None:
        """Test error verification response."""
        error = ErrorDetail(code="not_found", message="Invoice not found")
        response = VerifyInvoiceResponse(success=False, error=error)

        assert response.success is False
        assert response.error == error
        assert response.data is None

    def test_from_dict_with_payment(self) -> None:
        """Test creating response from dict with payment data."""
        dict_data: Dict[str, Any] = {
            "success": True,
            "data": {
                "id": "inv_123",
                "invoice_id": "INV-001",
                "original_amount": "100.00",
                "original_currency": "USD",
                "amount": 100.0,
                "currency": "USDC",
                "status": "completed",
                "paid": True,
                "created_at": "2024-01-01T00:00:00Z",
                "payment": {
                    "id": "pay_123",
                    "network": "polygon",
                    "token": "USDC",
                    "address": "0x1234",
                    "amount": 100.0,
                    "status": "confirmed",
                    "tx_hash": ["0xhash"],
                    "transaction_type": "payment",
                    "payer_email": "payer@example.com",
                    "created_at": "2024-01-01T00:05:00Z",
                },
            },
        }
        response = VerifyInvoiceResponse.from_dict(dict_data)

        assert response.success is True
        assert response.data is not None
        assert response.data.paid is True
        assert response.data.payment is not None
        assert response.data.payment.id == "pay_123"
