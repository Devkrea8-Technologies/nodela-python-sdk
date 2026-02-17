"""Pytest configuration and shared fixtures."""

from typing import Any, Dict
from unittest.mock import Mock

import pytest
from requests import Response

from nodela.client import NodelaClient
from nodela.utils.http import HTTPClient


@pytest.fixture
def api_key() -> str:
    """Return a test API key."""
    return "test_api_key_12345"


@pytest.fixture
def base_url() -> str:
    """Return the test base URL."""
    return "https://api.nodela.co"


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock response object."""
    response = Mock(spec=Response)
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    return response


@pytest.fixture
def http_client(api_key: str, base_url: str) -> HTTPClient:
    """Create an HTTPClient instance for testing."""
    return HTTPClient(
        base_url=base_url,
        api_key=api_key,
        timeout=30,
        max_retries=3,
    )


@pytest.fixture
def nodela_client(api_key: str) -> NodelaClient:
    """Create a NodelaClient instance for testing."""
    return NodelaClient(api_key=api_key, timeout=30, max_retries=3)


@pytest.fixture
def mock_invoice_response_data() -> Dict[str, Any]:
    """Return mock invoice creation response data."""
    return {
        "success": True,
        "data": {
            "id": "inv_test123",
            "invoice_id": "INV-2024-001",
            "original_amount": "100.00",
            "original_currency": "USD",
            "amount": "100.00",
            "currency": "USDC",
            "exchange_rate": "1.0",
            "webhook_url": "https://example.com/webhook",
            "customer": {"email": "test@example.com", "name": "Test User"},
            "checkout_url": "https://checkout.nodela.co/inv_test123",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00Z",
        },
    }


@pytest.fixture
def mock_verify_invoice_response_data() -> Dict[str, Any]:
    """Return mock invoice verification response data."""
    return {
        "success": True,
        "data": {
            "id": "inv_test123",
            "invoice_id": "INV-2024-001",
            "reference": "ORDER-001",
            "original_amount": "100.00",
            "original_currency": "USD",
            "amount": 100.0,
            "currency": "USDC",
            "exchange_rate": 1.0,
            "title": "Test Invoice",
            "description": "Test Description",
            "status": "completed",
            "paid": True,
            "customer": {"email": "test@example.com", "name": "Test User"},
            "created_at": "2024-01-01T00:00:00Z",
            "payment": {
                "id": "pay_test123",
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


@pytest.fixture
def mock_list_transactions_response_data() -> Dict[str, Any]:
    """Return mock list transactions response data."""
    return {
        "success": True,
        "data": {
            "transactions": [
                {
                    "id": "txn_test123",
                    "invoice_id": "INV-2024-001",
                    "reference": "ORDER-001",
                    "original_amount": 100.0,
                    "original_currency": "USD",
                    "amount": 100.0,
                    "currency": "USDC",
                    "exchange_rate": 1.0,
                    "title": "Test Transaction",
                    "description": "Test Description",
                    "status": "completed",
                    "paid": True,
                    "customer": {"email": "test@example.com", "name": "Test User"},
                    "created_at": "2024-01-01T00:00:00Z",
                    "payment": {
                        "id": "pay_test123",
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
                }
            ],
            "pagination": {"page": 1, "limit": 10, "total": 1, "total_pages": 1, "has_more": False},
        },
    }


@pytest.fixture
def mock_error_response_data() -> Dict[str, Any]:
    """Return mock error response data."""
    return {
        "success": False,
        "error": {"code": "validation_error", "message": "Invalid input parameters"},
    }
