# Models

All request and response data in the SDK is represented by Pydantic models. This provides automatic validation, type safety, and serialization.

## Base Model

All models extend a common `BaseModel` with the following configuration:

- **Extra fields allowed** - Unknown fields from the API are preserved, not rejected
- **Enum values used** - Enum fields serialize to their values
- **Assignment validation** - Fields are validated on assignment, not just construction
- **Alias population** - Fields can be populated by alias names

### Serialization Methods

Every model supports:

```python
# Convert to dictionary
data = model.to_dict()

# Create from dictionary
model = ModelClass.from_dict(data)
```

---

## Request Models

### `CreateInvoiceParams`

Parameters for creating a new invoice.

```python
from nodela import CreateInvoiceParams

params = CreateInvoiceParams(
    amount=100.0,          # float - Required
    currency="USD",        # SupportedCurrency - Required
    success_url=None,      # Optional[str]
    cancel_url=None,       # Optional[str]
    webhook_url=None,      # Optional[str]
    reference=None,        # Optional[str]
    customer=None,         # Optional[CustomerParams]
    title=None,            # Optional[str]
    description=None,      # Optional[str]
)
```

### `CustomerParams`

Customer information attached to an invoice.

```python
customer = CustomerParams(
    email="jane@example.com",   # str - Required
    name="Jane Doe",            # Optional[str]
)

# Or pass as a dict to CreateInvoiceParams:
params = CreateInvoiceParams(
    amount=50.0,
    currency="EUR",
    customer={"email": "jane@example.com", "name": "Jane Doe"},
)
```

---

## Response Models

### `CreateInvoiceResponse`

```python
class CreateInvoiceResponse:
    success: bool
    error: Optional[ErrorDetail]
    data: Optional[CreateInvoiceData]
```

### `CreateInvoiceData`

```python
class CreateInvoiceData:
    id: str                          # Internal record ID
    invoice_id: str                  # Nodela invoice ID
    original_amount: str             # Fiat amount as string
    original_currency: str           # Fiat currency code
    amount: str                      # Stablecoin amount as string
    currency: str                    # Stablecoin code
    exchange_rate: Optional[str]     # Conversion rate
    webhook_url: Optional[str]       # Webhook URL
    customer: Optional[CustomerInfo] # Customer details
    checkout_url: str                # Hosted checkout page
    status: Optional[str]           # Invoice status
    created_at: str                  # ISO 8601 timestamp
```

### `VerifyInvoiceResponse`

```python
class VerifyInvoiceResponse:
    success: bool
    data: Optional[VerifyInvoiceData]
    error: Optional[ErrorDetail]
```

### `VerifyInvoiceData`

```python
class VerifyInvoiceData:
    id: str
    invoice_id: str
    reference: Optional[str]
    original_amount: str
    original_currency: str
    amount: float
    currency: str
    exchange_rate: Optional[float]
    title: Optional[str]
    description: Optional[str]
    status: str
    paid: bool
    customer: Optional[CustomerInfo]
    created_at: str
    payment: Optional[PaymentInfo]
```

### `PaymentInfo`

```python
class PaymentInfo:
    id: str
    network: str              # Blockchain network
    token: str                # Token/stablecoin used
    address: str              # Receiving wallet address
    amount: float             # Amount received
    status: str               # Payment status
    tx_hash: List[str]        # Transaction hash(es)
    transaction_type: str     # Type of transaction
    payer_email: str          # Payer's email
    created_at: str           # ISO 8601 timestamp
```

### `ListTransactionsResponse`

```python
class ListTransactionsResponse:
    success: bool
    data: ListTransactionsData
```

### `ListTransactionsData`

```python
class ListTransactionsData:
    transactions: List[Transaction]
    pagination: Pagination
```

### `Transaction`

```python
class Transaction:
    id: str
    invoice_id: str
    reference: str
    original_amount: float
    original_currency: str
    amount: float
    currency: str
    exchange_rate: float
    title: str
    description: str
    status: str
    paid: bool
    customer: TransactionCustomer
    created_at: str
    payment: TransactionPayment
```

### `Pagination`

```python
class Pagination:
    page: int
    limit: int
    total: int
    total_pages: int
    has_more: bool
```

### `ErrorDetail`

```python
class ErrorDetail:
    code: str       # Error code
    message: str    # Human-readable error message
```

### `CustomerInfo`

```python
class CustomerInfo:
    email: str
    name: Optional[str]
```

### `TransactionCustomer`

```python
class TransactionCustomer:
    email: str
    name: str
```

### `TransactionPayment`

```python
class TransactionPayment:
    id: str
    network: str
    token: str
    address: str
    amount: float
    status: str
    tx_hash: List[str]
    transaction_type: str
    payer_email: str
    created_at: str
```
