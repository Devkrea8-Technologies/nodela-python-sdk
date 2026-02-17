# Invoices

The Invoices resource lets you create payment invoices and verify their payment status.

## Create an Invoice

```python
client.invoices.create(params: CreateInvoiceParams) -> CreateInvoiceResponse
```

Creates a new payment invoice and returns a hosted checkout URL.

### Parameters

`CreateInvoiceParams` fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | `float` | Yes | The payment amount in the specified fiat currency. |
| `currency` | `str` | Yes | ISO 4217 currency code (e.g., `"USD"`, `"EUR"`, `"NGN"`). See [Supported Currencies](supported-currencies.md). |
| `success_url` | `str` | No | URL to redirect the customer to after successful payment. |
| `cancel_url` | `str` | No | URL to redirect the customer to if they cancel. |
| `webhook_url` | `str` | No | URL to receive POST webhook notifications on payment status changes. |
| `reference` | `str` | No | Your internal order or reference identifier. |
| `customer` | `CustomerParams` | No | Customer information (see below). |
| `title` | `str` | No | Title displayed on the checkout page. |
| `description` | `str` | No | Description displayed on the checkout page. |

#### `CustomerParams`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | `str` | Yes | Customer's email address. |
| `name` | `str` | No | Customer's display name. |

### Example

```python
from nodela import NodelaClient, CreateInvoiceParams

client = NodelaClient(api_key="your_api_key")

params = CreateInvoiceParams(
    amount=100.00,
    currency="USD",
    success_url="https://yoursite.com/payment/success",
    cancel_url="https://yoursite.com/payment/cancel",
    webhook_url="https://yoursite.com/webhooks/nodela",
    reference="ORD-2024-001",
    title="Pro Plan Subscription",
    description="Monthly subscription to Pro Plan",
    customer={
        "email": "jane@example.com",
        "name": "Jane Doe",
    },
)

response = client.invoices.create(params)

if response.success:
    print(f"Invoice ID: {response.data.invoice_id}")
    print(f"Checkout:   {response.data.checkout_url}")
    print(f"Amount:     {response.data.amount} {response.data.currency}")
    print(f"Rate:       {response.data.exchange_rate}")
```

### Response

`CreateInvoiceResponse` fields:

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the request succeeded. |
| `error` | `ErrorDetail \| None` | Error details if the request failed. |
| `data` | `CreateInvoiceData \| None` | Invoice data if successful. |

`CreateInvoiceData` fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Internal record identifier. |
| `invoice_id` | `str` | The Nodela invoice ID (use this for verification). |
| `original_amount` | `str` | The amount in the original fiat currency. |
| `original_currency` | `str` | The original fiat currency code. |
| `amount` | `str` | The converted stablecoin amount. |
| `currency` | `str` | The stablecoin currency code. |
| `exchange_rate` | `str \| None` | The fiat-to-stablecoin conversion rate. |
| `webhook_url` | `str \| None` | The configured webhook URL. |
| `customer` | `CustomerInfo \| None` | Customer details. |
| `checkout_url` | `str` | The hosted checkout page URL. |
| `status` | `str \| None` | Current invoice status. |
| `created_at` | `str` | ISO 8601 creation timestamp. |

---

## Verify an Invoice

```python
client.invoices.verify(invoice_id: str) -> VerifyInvoiceResponse
```

Checks the payment status of an existing invoice.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | `str` | Yes | The invoice ID returned from `create()`. |

### Example

```python
result = client.invoices.verify("INV-abc123")

if result.success:
    data = result.data
    print(f"Status: {data.status}")
    print(f"Paid:   {data.paid}")

    if data.paid and data.payment:
        print(f"Network:  {data.payment.network}")
        print(f"Token:    {data.payment.token}")
        print(f"Tx Hash:  {data.payment.tx_hash}")
        print(f"Payer:    {data.payment.payer_email}")
```

### Response

`VerifyInvoiceResponse` fields:

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the request succeeded. |
| `data` | `VerifyInvoiceData \| None` | Invoice and payment data if successful. |
| `error` | `ErrorDetail \| None` | Error details if the request failed. |

`VerifyInvoiceData` fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Internal record identifier. |
| `invoice_id` | `str` | The Nodela invoice ID. |
| `reference` | `str \| None` | Your internal reference. |
| `original_amount` | `str` | Original fiat amount. |
| `original_currency` | `str` | Original fiat currency. |
| `amount` | `float` | Stablecoin amount. |
| `currency` | `str` | Stablecoin currency. |
| `exchange_rate` | `float \| None` | Conversion rate used. |
| `title` | `str \| None` | Invoice title. |
| `description` | `str \| None` | Invoice description. |
| `status` | `str` | Current invoice status. |
| `paid` | `bool` | Whether payment has been confirmed. |
| `customer` | `CustomerInfo \| None` | Customer details. |
| `created_at` | `str` | ISO 8601 creation timestamp. |
| `payment` | `PaymentInfo \| None` | Payment details (present when paid). |

`PaymentInfo` fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Payment record ID. |
| `network` | `str` | Blockchain network used. |
| `token` | `str` | Token/stablecoin used. |
| `address` | `str` | Receiving wallet address. |
| `amount` | `float` | Amount received. |
| `status` | `str` | Payment status. |
| `tx_hash` | `List[str]` | Blockchain transaction hash(es). |
| `transaction_type` | `str` | Type of transaction. |
| `payer_email` | `str` | Email of the payer. |
| `created_at` | `str` | ISO 8601 timestamp. |
