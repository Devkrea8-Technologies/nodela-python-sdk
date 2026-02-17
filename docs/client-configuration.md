# Client Configuration

The `NodelaClient` is the main entry point for all SDK operations. This page covers how to configure it for your use case.

## Constructor

```python
from nodela import NodelaClient

client = NodelaClient(
    api_key="your_api_key",   # Required (or set NODELA_API_KEY env var)
    timeout=30,               # Request timeout in seconds (default: 30)
    max_retries=3,            # Max retry attempts (default: 3)
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str \| None` | `None` | Your Nodela API key. If not provided, falls back to the `NODELA_API_KEY` environment variable. |
| `timeout` | `int` | `30` | HTTP request timeout in seconds. |
| `max_retries` | `int` | `3` | Maximum number of automatic retries for transient failures. |

## API Key Resolution

The SDK resolves the API key in this order:

1. The `api_key` argument passed to `NodelaClient()`
2. The `NODELA_API_KEY` environment variable
3. If neither is set, an `AuthenticationError` is raised immediately

## Retry Behavior

The SDK automatically retries failed requests with exponential backoff. Retries are triggered for the following HTTP status codes:

| Status Code | Meaning |
|-------------|---------|
| `429` | Rate limited |
| `500` | Internal server error |
| `502` | Bad gateway |
| `503` | Service unavailable |
| `504` | Gateway timeout |

Other errors (e.g., `400`, `401`, `404`) are not retried because they indicate client-side issues that won't resolve on retry.

### Customizing retries

```python
# Disable retries
client = NodelaClient(api_key="your_key", max_retries=0)

# More aggressive retries for unreliable networks
client = NodelaClient(api_key="your_key", max_retries=5, timeout=60)
```

## Resources

The client exposes two resource objects:

| Resource | Access | Description |
|----------|--------|-------------|
| `client.invoices` | `Invoices` | Create and verify payment invoices |
| `client.transactions` | `Transactions` | List and paginate transactions |

```python
# Invoice operations
client.invoices.create(params)
client.invoices.verify(invoice_id)

# Transaction operations
client.transactions.list(page=1, limit=20)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NODELA_API_KEY` | Your Nodela API key. Used as a fallback when `api_key` is not passed to the constructor. |
