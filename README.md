# Nodela Python SDK

The official Python SDK for the [Nodela](https://nodela.co) cryptocurrency payment API. Accept stablecoin payments in your Python applications with a clean, type-safe interface.

[![PyPI version](https://badge.fury.io/py/nodela.svg)](https://pypi.org/project/nodela/)
[![Python](https://img.shields.io/pypi/pyversions/nodela.svg)](https://pypi.org/project/nodela/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Simple, intuitive API for creating and verifying crypto payment invoices
- Support for **60+ fiat currencies** with automatic stablecoin conversion
- Built-in retry logic with exponential backoff
- Pydantic-powered request/response validation
- Comprehensive error handling with typed exceptions
- Full type annotations for IDE autocompletion and static analysis
- Environment variable support for API key management

## Installation

```bash
pip install nodela
```

**Requirements:** Python 3.8+

## Quick Start

### 1. Get your API key

Sign up at [nodela.co](https://nodela.co) and retrieve your API key from the dashboard.

### 2. Initialize the client

```python
from nodela import NodelaClient

# Pass the key directly
client = NodelaClient(api_key="your_api_key")

# Or set the NODELA_API_KEY environment variable and omit the argument
client = NodelaClient()
```

### 3. Create a payment invoice

```python
from nodela import NodelaClient, CreateInvoiceParams

client = NodelaClient(api_key="your_api_key")

params = CreateInvoiceParams(
    amount=50.00,
    currency="USD",
    success_url="https://yoursite.com/success",
    cancel_url="https://yoursite.com/cancel",
    webhook_url="https://yoursite.com/webhooks/nodela",
    reference="ORDER-123",
    title="Premium Plan",
    description="Monthly subscription",
    customer={
        "email": "customer@example.com",
        "name": "Jane Doe",
    },
)

response = client.invoices.create(params)

if response.success:
    print(f"Checkout URL: {response.data.checkout_url}")
    print(f"Invoice ID:   {response.data.invoice_id}")
```

### 4. Verify a payment

```python
result = client.invoices.verify("inv_abc123")

if result.success and result.data.paid:
    print(f"Payment confirmed! Status: {result.data.status}")
    if result.data.payment:
        print(f"Tx hash: {result.data.payment.tx_hash}")
```

### 5. List transactions

```python
response = client.transactions.list(page=1, limit=20)

for txn in response.data.transactions:
    print(f"{txn.invoice_id} | {txn.original_amount} {txn.original_currency} | {txn.status}")

print(f"Page {response.data.pagination.page} of {response.data.pagination.total_pages}")
```

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | `None` | Your Nodela API key. Falls back to `NODELA_API_KEY` env var. |
| `timeout` | `int` | `30` | Request timeout in seconds. |
| `max_retries` | `int` | `3` | Maximum retry attempts for failed requests. |

```python
client = NodelaClient(
    api_key="your_api_key",
    timeout=60,
    max_retries=5,
)
```

## API Reference

### `NodelaClient`

The main entry point. Provides access to all API resources.

#### `client.invoices.create(params)`

Create a new payment invoice.

**Parameters (`CreateInvoiceParams`):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | `float` | Yes | Payment amount in the specified currency. |
| `currency` | `str` | Yes | ISO 4217 currency code (see [supported currencies](#supported-currencies)). |
| `success_url` | `str` | No | URL to redirect to after successful payment. |
| `cancel_url` | `str` | No | URL to redirect to if payment is cancelled. |
| `webhook_url` | `str` | No | URL to receive payment status webhook notifications. |
| `reference` | `str` | No | Your internal order/reference ID. |
| `customer` | `dict` | No | Customer info with `email` (required) and `name` (optional). |
| `title` | `str` | No | Invoice title displayed on the checkout page. |
| `description` | `str` | No | Invoice description displayed on the checkout page. |

**Returns:** `CreateInvoiceResponse`

```python
response.success        # bool
response.data.id        # Internal record ID
response.data.invoice_id    # Nodela invoice ID
response.data.checkout_url  # Payment page URL
response.data.amount        # Converted stablecoin amount
response.data.currency      # Stablecoin currency
response.data.original_amount    # Original fiat amount
response.data.original_currency  # Original fiat currency
response.data.exchange_rate      # Conversion rate used
response.data.status        # Invoice status
response.data.created_at    # ISO 8601 timestamp
```

#### `client.invoices.verify(invoice_id)`

Verify the payment status of an invoice.

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `invoice_id` | `str` | Yes | The invoice ID to verify. |

**Returns:** `VerifyInvoiceResponse`

```python
response.success          # bool
response.data.paid        # Whether payment is confirmed
response.data.status      # Current invoice status
response.data.amount      # Stablecoin amount
response.data.payment     # Payment details (if paid)
response.data.payment.network      # Blockchain network
response.data.payment.token        # Token used
response.data.payment.tx_hash      # Transaction hash(es)
response.data.payment.payer_email  # Payer email
```

#### `client.transactions.list(page=None, limit=None)`

List your transactions with pagination.

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `page` | `int` | No | Page number (starts at 1). |
| `limit` | `int` | No | Results per page. |

**Returns:** `ListTransactionsResponse`

```python
response.data.transactions       # List[Transaction]
response.data.pagination.page    # Current page
response.data.pagination.total   # Total results
response.data.pagination.total_pages  # Total pages
response.data.pagination.has_more     # More pages available
```

## Error Handling

The SDK raises typed exceptions so you can handle specific failure modes:

```python
from nodela import (
    NodelaClient,
    CreateInvoiceParams,
    NodelaError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
    ServerError,
    NetworkError,
)

client = NodelaClient(api_key="your_api_key")

try:
    response = client.invoices.create(
        CreateInvoiceParams(amount=100, currency="USD")
    )
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Bad request: {e}")
except RateLimitError:
    print("Too many requests - slow down")
except NotFoundError:
    print("Resource not found")
except ServerError:
    print("Nodela server error - try again later")
except NetworkError:
    print("Network issue - check your connection")
except NodelaError as e:
    print(f"Unexpected API error ({e.status_code}): {e}")
```

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `AuthenticationError` | 401 | Invalid or missing API key |
| `ValidationError` | 400 / 422 | Invalid request parameters |
| `NotFoundError` | 404 | Invoice or resource not found |
| `RateLimitError` | 429 | Too many requests |
| `ServerError` | 5xx | Nodela server error |
| `NetworkError` | N/A | Connection timeout or failure |

All exceptions inherit from `NodelaError`, which exposes `status_code` and `response` attributes.

## Supported Currencies

The SDK supports 60+ fiat currencies that are automatically converted to stablecoins at checkout:

| Region | Currencies |
|--------|-----------|
| **Americas** | USD, CAD, MXN, BRL, ARS, CLP, COP, PEN, JMD, TTD |
| **Europe** | EUR, GBP, CHF, SEK, NOK, DKK, PLN, CZK, HUF, RON, BGN, HRK, ISK, TRY, RUB, UAH |
| **Africa** | NGN, ZAR, KES, GHS, EGP, MAD, TZS, UGX, XOF, XAF, ETB |
| **Asia** | JPY, CNY, INR, KRW, IDR, MYR, THB, PHP, VND, SGD, HKD, TWD, BDT, PKR, LKR |
| **Middle East** | AED, SAR, QAR, KWD, BHD, OMR, ILS, JOD |
| **Oceania** | AUD, NZD, FJD |

You can access the full list programmatically:

```python
from nodela import SUPPORTED_CURRENCIES
print(SUPPORTED_CURRENCIES)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NODELA_API_KEY` | Your Nodela API key. Used when `api_key` is not passed to `NodelaClient`. |

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

## License

This project is licensed under the [MIT License](LICENSE).

## Links

- [Nodela Website](https://nodela.co)
- [API Documentation](https://docs.nodela.co)
- [Python SDK Docs](https://docs.nodela.co/sdks/python)
- [GitHub Repository](https://github.com/Devkrea8-Technologies/nodela-python-sdk)
- [Issue Tracker](https://github.com/Devkrea8-Technologies/nodela-python-sdk/issues)
- [PyPI Package](https://pypi.org/project/nodela/)
