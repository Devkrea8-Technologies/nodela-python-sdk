"""Unit tests for Transactions resource."""

from typing import Any, Dict
from unittest.mock import patch

from nodela.models.transaction import ListTransactionsResponse
from nodela.resources.transactions import Transactions
from nodela.utils.http import HTTPClient


class TestTransactionsResourceInitialization:
    """Test cases for Transactions resource initialization."""

    def test_initialization(self, http_client: HTTPClient) -> None:
        """Test Transactions resource initialization."""
        transactions = Transactions(http_client)

        assert transactions._http == http_client
        assert transactions.RESOURCE_PATH == "v1/transactions"

    def test_resource_path_is_correct(self, http_client: HTTPClient) -> None:
        """Test that resource path is correctly set."""
        transactions = Transactions(http_client)

        assert transactions.RESOURCE_PATH == "v1/transactions"


class TestTransactionsList:
    """Test cases for listing transactions."""

    def test_list_without_params(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test listing transactions without parameters."""
        transactions = Transactions(http_client)

        with patch.object(http_client, "get", return_value=mock_list_transactions_response_data):
            response = transactions.list()

        assert isinstance(response, ListTransactionsResponse)
        assert response.success is True
        assert response.data is not None

    def test_list_calls_correct_endpoint(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test that list calls the correct API endpoint."""
        transactions = Transactions(http_client)

        with patch.object(
            http_client, "get", return_value=mock_list_transactions_response_data
        ) as mock_get:
            transactions.list()

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "v1/transactions"

    def test_list_with_page_param(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test listing transactions with page parameter."""
        transactions = Transactions(http_client)

        with patch.object(
            http_client, "get", return_value=mock_list_transactions_response_data
        ) as mock_get:
            transactions.list(page=2)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params is not None
        assert params["page"] == 2

    def test_list_with_limit_param(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test listing transactions with limit parameter."""
        transactions = Transactions(http_client)

        with patch.object(
            http_client, "get", return_value=mock_list_transactions_response_data
        ) as mock_get:
            transactions.list(limit=25)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params is not None
        assert params["limit"] == 25

    def test_list_with_both_params(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test listing transactions with both page and limit."""
        transactions = Transactions(http_client)

        with patch.object(
            http_client, "get", return_value=mock_list_transactions_response_data
        ) as mock_get:
            transactions.list(page=3, limit=50)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params is not None
        assert params["page"] == 3
        assert params["limit"] == 50

    def test_list_without_params_passes_none(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test that list without params passes None for params."""
        transactions = Transactions(http_client)

        with patch.object(
            http_client, "get", return_value=mock_list_transactions_response_data
        ) as mock_get:
            transactions.list()

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params is None

    def test_list_response_has_transactions(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test that list response contains transactions."""
        transactions = Transactions(http_client)

        with patch.object(http_client, "get", return_value=mock_list_transactions_response_data):
            response = transactions.list()

        assert response.data.transactions is not None
        assert len(response.data.transactions) == 1
        assert response.data.transactions[0].id == "txn_test123"

    def test_list_response_has_pagination(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test that list response contains pagination info."""
        transactions = Transactions(http_client)

        with patch.object(http_client, "get", return_value=mock_list_transactions_response_data):
            response = transactions.list()

        assert response.data.pagination is not None
        assert response.data.pagination.page == 1
        assert response.data.pagination.limit == 10
        assert response.data.pagination.total == 1
        assert response.data.pagination.total_pages == 1
        assert response.data.pagination.has_more is False

    def test_list_empty_transactions(self, http_client: HTTPClient) -> None:
        """Test listing when there are no transactions."""
        empty_response: Dict[str, Any] = {
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

        transactions = Transactions(http_client)

        with patch.object(http_client, "get", return_value=empty_response):
            response = transactions.list()

        assert response.success is True
        assert len(response.data.transactions) == 0
        assert response.data.pagination.total == 0

    def test_list_multiple_transactions(self, http_client: HTTPClient) -> None:
        """Test listing with multiple transactions."""
        multi_response: Dict[str, Any] = {
            "success": True,
            "data": {
                "transactions": [
                    {
                        "id": f"txn_test{i}",
                        "invoice_id": f"INV-{i}",
                        "reference": f"ORDER-{i}",
                        "original_amount": 100.0 * i,
                        "original_currency": "USD",
                        "amount": 100.0 * i,
                        "currency": "USDC",
                        "exchange_rate": 1.0,
                        "title": f"Transaction {i}",
                        "description": "Description",
                        "status": "completed",
                        "paid": True,
                        "customer": {"email": f"user{i}@example.com", "name": f"User {i}"},
                        "created_at": "2024-01-01T00:00:00Z",
                        "payment": {
                            "id": f"pay_test{i}",
                            "network": "polygon",
                            "token": "USDC",
                            "address": "0x1234",
                            "amount": 100.0 * i,
                            "status": "confirmed",
                            "tx_hash": [f"0xhash{i}"],
                            "transaction_type": "payment",
                            "payer_email": f"payer{i}@example.com",
                            "created_at": "2024-01-01T00:05:00Z",
                        },
                    }
                    for i in range(1, 6)
                ],
                "pagination": {
                    "page": 1,
                    "limit": 10,
                    "total": 5,
                    "total_pages": 1,
                    "has_more": False,
                },
            },
        }

        transactions = Transactions(http_client)

        with patch.object(http_client, "get", return_value=multi_response):
            response = transactions.list()

        assert len(response.data.transactions) == 5
        assert response.data.pagination.total == 5

    def test_list_with_pagination_has_more(self, http_client: HTTPClient) -> None:
        """Test listing with pagination indicating more pages."""
        paginated_response: Dict[str, Any] = {
            "success": True,
            "data": {
                "transactions": [
                    {
                        "id": "txn_test1",
                        "invoice_id": "INV-001",
                        "reference": "ORDER-001",
                        "original_amount": 100.0,
                        "original_currency": "USD",
                        "amount": 100.0,
                        "currency": "USDC",
                        "exchange_rate": 1.0,
                        "title": "Transaction",
                        "description": "Description",
                        "status": "completed",
                        "paid": True,
                        "customer": {"email": "user@example.com", "name": "User"},
                        "created_at": "2024-01-01T00:00:00Z",
                        "payment": {
                            "id": "pay_test1",
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
                "pagination": {
                    "page": 1,
                    "limit": 1,
                    "total": 100,
                    "total_pages": 100,
                    "has_more": True,
                },
            },
        }

        transactions = Transactions(http_client)

        with patch.object(http_client, "get", return_value=paginated_response):
            response = transactions.list(page=1, limit=1)

        assert response.data.pagination.has_more is True
        assert response.data.pagination.total_pages == 100

    def test_list_with_page_zero(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test listing with page 0 (edge case)."""
        transactions = Transactions(http_client)

        with patch.object(
            http_client, "get", return_value=mock_list_transactions_response_data
        ) as mock_get:
            transactions.list(page=0)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["page"] == 0

    def test_list_with_large_limit(
        self, http_client: HTTPClient, mock_list_transactions_response_data: Dict[str, Any]
    ) -> None:
        """Test listing with a large limit value."""
        transactions = Transactions(http_client)

        with patch.object(
            http_client, "get", return_value=mock_list_transactions_response_data
        ) as mock_get:
            transactions.list(limit=1000)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["limit"] == 1000


class TestTransactionsBuildEndpoint:
    """Test cases for endpoint building."""

    def test_build_endpoint(self, http_client: HTTPClient) -> None:
        """Test _build_endpoint method."""
        transactions = Transactions(http_client)

        endpoint = transactions._build_endpoint("v1/transactions", "filter")

        assert endpoint == "v1/transactions/filter"

    def test_build_endpoint_single_part(self, http_client: HTTPClient) -> None:
        """Test building endpoint with single part."""
        transactions = Transactions(http_client)

        endpoint = transactions._build_endpoint("v1/transactions")

        assert endpoint == "v1/transactions"


class TestTransactionsIntegration:
    """Integration-style tests for Transactions resource."""

    def test_paginated_listing_flow(self, http_client: HTTPClient) -> None:
        """Test pagination flow through multiple pages."""
        transactions = Transactions(http_client)

        # First page
        page1_response: Dict[str, Any] = {
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
                        "title": "Transaction",
                        "description": "Description",
                        "status": "completed",
                        "paid": True,
                        "customer": {"email": "user@example.com", "name": "User"},
                        "created_at": "2024-01-01T00:00:00Z",
                        "payment": {
                            "id": f"pay_{i}",
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

        with patch.object(http_client, "get", return_value=page1_response):
            response1 = transactions.list(page=1, limit=10)

        assert len(response1.data.transactions) == 10
        assert response1.data.pagination.has_more is True

        # Second page
        page2_response: Dict[str, Any] = {
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
                        "title": "Transaction",
                        "description": "Description",
                        "status": "completed",
                        "paid": True,
                        "customer": {"email": "user@example.com", "name": "User"},
                        "created_at": "2024-01-01T00:00:00Z",
                        "payment": {
                            "id": f"pay_{i}",
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
                    for i in range(11, 21)
                ],
                "pagination": {
                    "page": 2,
                    "limit": 10,
                    "total": 25,
                    "total_pages": 3,
                    "has_more": True,
                },
            },
        }

        with patch.object(http_client, "get", return_value=page2_response):
            response2 = transactions.list(page=2, limit=10)

        assert response2.data.pagination.page == 2
        assert response2.data.pagination.has_more is True

    def test_different_limit_sizes(self, http_client: HTTPClient) -> None:
        """Test listing with different limit sizes."""
        transactions = Transactions(http_client)
        limits = [5, 10, 20, 50, 100]

        for limit in limits:
            response_data: Dict[str, Any] = {
                "success": True,
                "data": {
                    "transactions": [],
                    "pagination": {
                        "page": 1,
                        "limit": limit,
                        "total": 0,
                        "total_pages": 0,
                        "has_more": False,
                    },
                },
            }

            with patch.object(http_client, "get", return_value=response_data):
                response = transactions.list(limit=limit)

            assert response.data.pagination.limit == limit
