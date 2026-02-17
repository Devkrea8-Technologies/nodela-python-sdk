# Getting Started

Learn how to install the Nodela Python SDK and make your first payment invoice.

## Prerequisites

- Python 3.8 or higher
- A Nodela account with an API key ([sign up here](https://nodela.co))

## Installation

Install the SDK from PyPI:

```bash
pip install nodela
```

Or add it to your `requirements.txt`:

```
nodela>=1.0.0
```

## Authentication

The SDK authenticates using your Nodela API key. You can provide it in two ways:

### Option 1: Pass directly

```python
from nodela import NodelaClient

client = NodelaClient(api_key="nod_live_your_api_key_here")
```

### Option 2: Environment variable

Set the `NODELA_API_KEY` environment variable:

```bash
export NODELA_API_KEY="nod_live_your_api_key_here"
```

Then initialize without arguments:

```python
from nodela import NodelaClient

client = NodelaClient()
```

> If neither is provided, the SDK raises an `AuthenticationError` immediately.

## Your First Invoice

Create a payment invoice in just a few lines:

```python
from nodela import NodelaClient, CreateInvoiceParams

client = NodelaClient(api_key="your_api_key")

params = CreateInvoiceParams(
    amount=25.00,
    currency="USD",
    reference="ORDER-001",
)

response = client.invoices.create(params)

if response.success:
    # Redirect the customer to the checkout page
    print(f"Checkout URL: {response.data.checkout_url}")
    print(f"Invoice ID: {response.data.invoice_id}")
else:
    print(f"Error: {response.error.message}")
```

The `checkout_url` is a hosted payment page where your customer completes the stablecoin payment.

## Verifying Payment

After the customer pays, verify the invoice status:

```python
result = client.invoices.verify(response.data.invoice_id)

if result.success and result.data.paid:
    print("Payment confirmed!")
else:
    print(f"Status: {result.data.status}")
```

## Next Steps

- [Client Configuration](client-configuration.md) - Customize timeouts and retries
- [Invoices](invoices.md) - Full invoice creation and verification reference
- [Error Handling](error-handling.md) - Handle failures gracefully
- [Examples](examples.md) - Real-world integration patterns
