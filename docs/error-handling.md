# Error Handling

The SDK provides a typed exception hierarchy so you can handle different failure modes precisely.

## Exception Hierarchy

All exceptions inherit from `NodelaError`:

```
NodelaError (base)
├── AuthenticationError   (401)
├── ValidationError       (400, 422)
├── NotFoundError         (404)
├── RateLimitError        (429)
├── ServerError           (5xx)
└── NetworkError          (connection/timeout)
```

## Exception Reference

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `NodelaError` | Any | Base exception for all SDK errors. |
| `AuthenticationError` | 401 | Invalid or missing API key. |
| `ValidationError` | 400 / 422 | Invalid request parameters or payload. |
| `NotFoundError` | 404 | The requested resource (e.g., invoice) was not found. |
| `RateLimitError` | 429 | API rate limit exceeded. |
| `ServerError` | 5xx | Nodela server-side error. |
| `NetworkError` | N/A | Connection failure or request timeout. |

## Exception Attributes

Every exception exposes these attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Human-readable error description (also the string representation). |
| `status_code` | `int \| None` | HTTP status code, if available. `None` for network errors. |
| `response` | `Any \| None` | Raw API response body, if available. |

```python
except NodelaError as e:
    print(e)              # Error message
    print(e.status_code)  # HTTP status code or None
    print(e.response)     # Raw response body or None
```

## Usage Patterns

### Catch-all

Catch any SDK error with the base exception:

```python
from nodela import NodelaClient, NodelaError

client = NodelaClient(api_key="your_key")

try:
    response = client.invoices.verify("INV-123")
except NodelaError as e:
    print(f"Something went wrong: {e}")
```

### Granular handling

Handle each error type differently:

```python
from nodela import (
    NodelaClient,
    CreateInvoiceParams,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
    ServerError,
    NetworkError,
    NodelaError,
)

client = NodelaClient(api_key="your_key")

try:
    params = CreateInvoiceParams(amount=100, currency="USD")
    response = client.invoices.create(params)
except AuthenticationError:
    # API key is invalid - check your credentials
    log.error("Authentication failed. Check your API key.")
except ValidationError as e:
    # Bad request parameters
    log.error(f"Invalid parameters: {e}")
except RateLimitError:
    # Too many requests - implement backoff
    log.warning("Rate limited. Retrying after delay...")
except NotFoundError:
    # Resource doesn't exist
    log.error("Invoice not found.")
except ServerError:
    # Nodela is having issues - retry later
    log.error("Server error. Please retry.")
except NetworkError:
    # Connection or timeout issue
    log.error("Network error. Check your connection.")
except NodelaError as e:
    # Catch-all for any other SDK error
    log.error(f"Unexpected error ({e.status_code}): {e}")
```

### Initialization errors

`AuthenticationError` is raised at client creation if no API key is available:

```python
from nodela import NodelaClient, AuthenticationError

try:
    client = NodelaClient()  # No api_key and no NODELA_API_KEY env var
except AuthenticationError:
    print("Please set your API key")
```

## Automatic Retries

The SDK automatically retries requests that fail with transient errors:

| Retried Status Codes | Description |
|----------------------|-------------|
| 429 | Rate limited |
| 500 | Internal server error |
| 502 | Bad gateway |
| 503 | Service unavailable |
| 504 | Gateway timeout |

Retries use exponential backoff. The maximum number of retries is configurable via `max_retries` (default: 3). If all retries are exhausted, the corresponding exception is raised.

Non-retryable errors (400, 401, 404, 422) are raised immediately.
