"""Unit tests for transaction models."""

from typing import Any, Dict, List

import pytest
from pydantic import ValidationError as PydanticValidationError

from nodela.models.transaction import (
    ListTransactionsData,
    ListTransactionsResponse,
    Pagination,
    Transaction,
    TransactionCustomer,
    TransactionPayment,
)


class TestTransactionCustomer:
    """Test cases for TransactionCustomer model."""

    def test_initialization(self) -> None:
        """Test TransactionCustomer initialization."""
        customer = TransactionCustomer(email="test@example.com", name="Test User")
        assert customer.email == "test@example.com"
        assert customer.name == "Test User"

    def test_missing_email_raises_error(self) -> None:
        """Test that missing email raises validation error."""
        with pytest.raises(PydanticValidationError):
            TransactionCustomer(name="Test User")  # type: ignore

    def test_missing_name_raises_error(self) -> None:
        """Test that missing name raises validation error."""
        with pytest.raises(PydanticValidationError):
            TransactionCustomer(email="test@example.com")  # type: ignore

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        customer = TransactionCustomer(email="test@example.com", name="Test User")
        result = customer.to_dict()
        assert result == {"email": "test@example.com", "name": "Test User"}

    def test_from_dict(self) -> None:
        """Test from_dict method."""
        data: Dict[str, str] = {"email": "test@example.com", "name": "Test User"}
        customer = TransactionCustomer.from_dict(data)
        assert customer.email == "test@example.com"
        assert customer.name == "Test User"


class TestTransactionPayment:
    """Test cases for TransactionPayment model."""

    def test_initialization(self) -> None:
        """Test TransactionPayment initialization."""
        payment = TransactionPayment(
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
        """Test payment with multiple transaction hashes."""
        tx_hashes: List[str] = ["0xhash1", "0xhash2", "0xhash3"]
        payment = TransactionPayment(
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

    def test_empty_tx_hash_list(self) -> None:
        """Test payment with empty transaction hash list."""
        payment = TransactionPayment(
            id="pay_123",
            network="polygon",
            token="USDC",
            address="0xaddress",
            amount=100.0,
            status="pending",
            tx_hash=[],
            transaction_type="payment",
            payer_email="test@example.com",
            created_at="2024-01-01T00:00:00Z",
        )

        assert payment.tx_hash == []
        assert len(payment.tx_hash) == 0

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        payment = TransactionPayment(
            id="pay_123",
            network="polygon",
            token="USDC",
            address="0x1234",
            amount=100.0,
            status="confirmed",
            tx_hash=["0xhash"],
            transaction_type="payment",
            payer_email="payer@example.com",
            created_at="2024-01-01T00:00:00Z",
        )
        result = payment.to_dict()

        assert result["id"] == "pay_123"
        assert result["network"] == "polygon"
        assert result["amount"] == 100.0

    def test_from_dict(self) -> None:
        """Test from_dict method."""
        data: Dict[str, Any] = {
            "id": "pay_123",
            "network": "polygon",
            "token": "USDC",
            "address": "0x1234",
            "amount": 100.0,
            "status": "confirmed",
            "tx_hash": ["0xhash"],
            "transaction_type": "payment",
            "payer_email": "payer@example.com",
            "created_at": "2024-01-01T00:00:00Z",
        }
        payment = TransactionPayment.from_dict(data)

        assert payment.id == "pay_123"
        assert payment.network == "polygon"


class TestTransaction:
    """Test cases for Transaction model."""

    def test_initialization(self) -> None:
        """Test Transaction initialization."""
        customer = TransactionCustomer(email="test@example.com", name="Test User")
        payment = TransactionPayment(
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

        transaction = Transaction(
            id="txn_123",
            invoice_id="INV-001",
            reference="ORDER-001",
            original_amount=100.0,
            original_currency="USD",
            amount=100.0,
            currency="USDC",
            exchange_rate=1.0,
            title="Test Transaction",
            description="Test Description",
            status="completed",
            paid=True,
            customer=customer,
            created_at="2024-01-01T00:00:00Z",
            payment=payment,
        )

        assert transaction.id == "txn_123"
        assert transaction.invoice_id == "INV-001"
        assert transaction.reference == "ORDER-001"
        assert transaction.original_amount == 100.0
        assert transaction.original_currency == "USD"
        assert transaction.amount == 100.0
        assert transaction.currency == "USDC"
        assert transaction.exchange_rate == 1.0
        assert transaction.title == "Test Transaction"
        assert transaction.description == "Test Description"
        assert transaction.status == "completed"
        assert transaction.paid is True
        assert transaction.customer == customer
        assert transaction.created_at == "2024-01-01T00:00:00Z"
        assert transaction.payment == payment

    def test_missing_required_fields_raises_error(self) -> None:
        """Test that missing required fields raise validation errors."""
        with pytest.raises(PydanticValidationError):
            Transaction(  # type: ignore
                id="txn_123",
                invoice_id="INV-001",
                # Missing many required fields
            )

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        customer = TransactionCustomer(email="test@example.com", name="Test User")
        payment = TransactionPayment(
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

        transaction = Transaction(
            id="txn_123",
            invoice_id="INV-001",
            reference="ORDER-001",
            original_amount=100.0,
            original_currency="USD",
            amount=100.0,
            currency="USDC",
            exchange_rate=1.0,
            title="Test",
            description="Desc",
            status="completed",
            paid=True,
            customer=customer,
            created_at="2024-01-01T00:00:00Z",
            payment=payment,
        )

        result = transaction.to_dict()

        assert result["id"] == "txn_123"
        assert result["invoice_id"] == "INV-001"
        assert result["paid"] is True
        assert "customer" in result
        assert "payment" in result

    def test_from_dict(self) -> None:
        """Test from_dict method."""
        data: Dict[str, Any] = {
            "id": "txn_123",
            "invoice_id": "INV-001",
            "reference": "ORDER-001",
            "original_amount": 100.0,
            "original_currency": "USD",
            "amount": 100.0,
            "currency": "USDC",
            "exchange_rate": 1.0,
            "title": "Test",
            "description": "Desc",
            "status": "completed",
            "paid": True,
            "customer": {"email": "test@example.com", "name": "Test User"},
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
        }

        transaction = Transaction.from_dict(data)

        assert transaction.id == "txn_123"
        assert transaction.invoice_id == "INV-001"
        assert isinstance(transaction.customer, TransactionCustomer)
        assert isinstance(transaction.payment, TransactionPayment)


class TestPagination:
    """Test cases for Pagination model."""

    def test_initialization(self) -> None:
        """Test Pagination initialization."""
        pagination = Pagination(page=1, limit=10, total=50, total_pages=5, has_more=True)

        assert pagination.page == 1
        assert pagination.limit == 10
        assert pagination.total == 50
        assert pagination.total_pages == 5
        assert pagination.has_more is True

    def test_no_more_pages(self) -> None:
        """Test pagination when on last page."""
        pagination = Pagination(page=5, limit=10, total=50, total_pages=5, has_more=False)

        assert pagination.page == 5
        assert pagination.has_more is False

    def test_first_page(self) -> None:
        """Test pagination on first page."""
        pagination = Pagination(page=1, limit=20, total=100, total_pages=5, has_more=True)

        assert pagination.page == 1
        assert pagination.has_more is True

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        pagination = Pagination(page=2, limit=15, total=75, total_pages=5, has_more=True)
        result = pagination.to_dict()

        assert result == {"page": 2, "limit": 15, "total": 75, "total_pages": 5, "has_more": True}

    def test_from_dict(self) -> None:
        """Test from_dict method."""
        data: Dict[str, Any] = {
            "page": 3,
            "limit": 25,
            "total": 200,
            "total_pages": 8,
            "has_more": True,
        }
        pagination = Pagination.from_dict(data)

        assert pagination.page == 3
        assert pagination.limit == 25
        assert pagination.total == 200


class TestListTransactionsData:
    """Test cases for ListTransactionsData model."""

    def test_initialization_empty_list(self) -> None:
        """Test initialization with empty transactions list."""
        pagination = Pagination(page=1, limit=10, total=0, total_pages=0, has_more=False)
        data = ListTransactionsData(transactions=[], pagination=pagination)

        assert data.transactions == []
        assert len(data.transactions) == 0
        assert data.pagination == pagination

    def test_initialization_with_transactions(self) -> None:
        """Test initialization with transactions."""
        customer = TransactionCustomer(email="test@example.com", name="Test User")
        payment = TransactionPayment(
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

        transaction = Transaction(
            id="txn_123",
            invoice_id="INV-001",
            reference="ORDER-001",
            original_amount=100.0,
            original_currency="USD",
            amount=100.0,
            currency="USDC",
            exchange_rate=1.0,
            title="Test",
            description="Desc",
            status="completed",
            paid=True,
            customer=customer,
            created_at="2024-01-01T00:00:00Z",
            payment=payment,
        )

        pagination = Pagination(page=1, limit=10, total=1, total_pages=1, has_more=False)

        data = ListTransactionsData(transactions=[transaction], pagination=pagination)

        assert len(data.transactions) == 1
        assert data.transactions[0] == transaction
        assert data.pagination == pagination

    def test_from_dict(self) -> None:
        """Test from_dict method."""
        dict_data: Dict[str, Any] = {
            "transactions": [
                {
                    "id": "txn_123",
                    "invoice_id": "INV-001",
                    "reference": "ORDER-001",
                    "original_amount": 100.0,
                    "original_currency": "USD",
                    "amount": 100.0,
                    "currency": "USDC",
                    "exchange_rate": 1.0,
                    "title": "Test",
                    "description": "Desc",
                    "status": "completed",
                    "paid": True,
                    "customer": {"email": "test@example.com", "name": "Test User"},
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
                }
            ],
            "pagination": {"page": 1, "limit": 10, "total": 1, "total_pages": 1, "has_more": False},
        }

        data = ListTransactionsData.from_dict(dict_data)

        assert len(data.transactions) == 1
        assert data.transactions[0].id == "txn_123"
        assert data.pagination.page == 1


class TestListTransactionsResponse:
    """Test cases for ListTransactionsResponse model."""

    def test_successful_response(self) -> None:
        """Test successful list transactions response."""
        pagination = Pagination(page=1, limit=10, total=0, total_pages=0, has_more=False)
        list_data = ListTransactionsData(transactions=[], pagination=pagination)
        response = ListTransactionsResponse(success=True, data=list_data)

        assert response.success is True
        assert response.data == list_data

    def test_response_with_transactions(self) -> None:
        """Test response with actual transactions."""
        customer = TransactionCustomer(email="test@example.com", name="Test User")
        payment = TransactionPayment(
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

        transaction = Transaction(
            id="txn_123",
            invoice_id="INV-001",
            reference="ORDER-001",
            original_amount=100.0,
            original_currency="USD",
            amount=100.0,
            currency="USDC",
            exchange_rate=1.0,
            title="Test",
            description="Desc",
            status="completed",
            paid=True,
            customer=customer,
            created_at="2024-01-01T00:00:00Z",
            payment=payment,
        )

        pagination = Pagination(page=1, limit=10, total=1, total_pages=1, has_more=False)

        list_data = ListTransactionsData(transactions=[transaction], pagination=pagination)
        response = ListTransactionsResponse(success=True, data=list_data)

        assert response.success is True
        assert len(response.data.transactions) == 1
        assert response.data.transactions[0].id == "txn_123"

    def test_from_dict(self) -> None:
        """Test from_dict method."""
        dict_data: Dict[str, Any] = {
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

        response = ListTransactionsResponse.from_dict(dict_data)

        assert response.success is True
        assert len(response.data.transactions) == 0

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        pagination = Pagination(page=1, limit=10, total=0, total_pages=0, has_more=False)
        list_data = ListTransactionsData(transactions=[], pagination=pagination)
        response = ListTransactionsResponse(success=True, data=list_data)

        result = response.to_dict()

        assert result["success"] is True
        assert "data" in result
        assert "transactions" in result["data"]
        assert "pagination" in result["data"]
