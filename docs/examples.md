# Examples

Real-world integration patterns and complete usage examples for the Nodela Python SDK.

## Basic Payment Flow

A minimal end-to-end payment integration:

```python
from nodela import NodelaClient, CreateInvoiceParams

client = NodelaClient(api_key="your_api_key")

# 1. Create an invoice
params = CreateInvoiceParams(
    amount=29.99,
    currency="USD",
    reference="ORDER-001",
)
invoice = client.invoices.create(params)

# 2. Redirect the customer to the checkout URL
checkout_url = invoice.data.checkout_url
print(f"Send customer to: {checkout_url}")

# 3. Later, verify the payment
result = client.invoices.verify(invoice.data.invoice_id)
if result.data.paid:
    print("Payment confirmed!")
```

## Flask Integration

Accept payments in a Flask web application:

```python
from flask import Flask, request, redirect, jsonify
from nodela import NodelaClient, CreateInvoiceParams, NodelaError

app = Flask(__name__)
client = NodelaClient()  # Uses NODELA_API_KEY env var


@app.route("/checkout", methods=["POST"])
def create_checkout():
    data = request.json

    params = CreateInvoiceParams(
        amount=data["amount"],
        currency=data.get("currency", "USD"),
        success_url="https://yoursite.com/success",
        cancel_url="https://yoursite.com/cancel",
        webhook_url="https://yoursite.com/webhooks/nodela",
        reference=data.get("order_id"),
        customer={"email": data["email"]},
    )

    try:
        response = client.invoices.create(params)
        return jsonify({
            "checkout_url": response.data.checkout_url,
            "invoice_id": response.data.invoice_id,
        })
    except NodelaError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/webhooks/nodela", methods=["POST"])
def handle_webhook():
    payload = request.json
    invoice_id = payload.get("invoice_id")

    # Verify the payment independently
    result = client.invoices.verify(invoice_id)

    if result.data.paid:
        # Update your order status in the database
        print(f"Order paid: {result.data.reference}")

    return "", 200


@app.route("/verify/<invoice_id>")
def verify_payment(invoice_id):
    result = client.invoices.verify(invoice_id)
    return jsonify({
        "paid": result.data.paid,
        "status": result.data.status,
    })
```

## Django Integration

Accept payments in a Django application:

```python
# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from nodela import NodelaClient, CreateInvoiceParams, NodelaError

client = NodelaClient()  # Uses NODELA_API_KEY env var


@require_POST
def create_checkout(request):
    data = json.loads(request.body)

    params = CreateInvoiceParams(
        amount=data["amount"],
        currency=data.get("currency", "USD"),
        success_url="https://yoursite.com/success",
        cancel_url="https://yoursite.com/cancel",
        webhook_url="https://yoursite.com/webhooks/nodela",
        reference=data.get("order_id"),
        customer={"email": data["email"]},
    )

    try:
        response = client.invoices.create(params)
        return JsonResponse({
            "checkout_url": response.data.checkout_url,
            "invoice_id": response.data.invoice_id,
        })
    except NodelaError as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_POST
def handle_webhook(request):
    payload = json.loads(request.body)
    invoice_id = payload.get("invoice_id")

    result = client.invoices.verify(invoice_id)

    if result.data.paid:
        # Update your order in the database
        pass

    return JsonResponse({"status": "ok"})


@require_GET
def verify_payment(request, invoice_id):
    result = client.invoices.verify(invoice_id)
    return JsonResponse({
        "paid": result.data.paid,
        "status": result.data.status,
    })
```

## FastAPI Integration

Accept payments in a FastAPI application:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel as PydanticBaseModel
from nodela import NodelaClient, CreateInvoiceParams, NodelaError

app = FastAPI()
client = NodelaClient()  # Uses NODELA_API_KEY env var


class CheckoutRequest(PydanticBaseModel):
    amount: float
    currency: str = "USD"
    order_id: str | None = None
    email: str


@app.post("/checkout")
async def create_checkout(req: CheckoutRequest):
    params = CreateInvoiceParams(
        amount=req.amount,
        currency=req.currency,
        success_url="https://yoursite.com/success",
        cancel_url="https://yoursite.com/cancel",
        webhook_url="https://yoursite.com/webhooks/nodela",
        reference=req.order_id,
        customer={"email": req.email},
    )

    try:
        response = client.invoices.create(params)
        return {
            "checkout_url": response.data.checkout_url,
            "invoice_id": response.data.invoice_id,
        }
    except NodelaError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/nodela")
async def handle_webhook(payload: dict):
    invoice_id = payload.get("invoice_id")
    result = client.invoices.verify(invoice_id)

    if result.data.paid:
        # Update order status
        pass

    return {"status": "ok"}


@app.get("/verify/{invoice_id}")
async def verify_payment(invoice_id: str):
    result = client.invoices.verify(invoice_id)
    return {
        "paid": result.data.paid,
        "status": result.data.status,
    }
```

## E-Commerce Checkout with Customer Details

Create a detailed invoice with full customer information:

```python
from nodela import NodelaClient, CreateInvoiceParams

client = NodelaClient(api_key="your_api_key")

params = CreateInvoiceParams(
    amount=149.99,
    currency="EUR",
    success_url="https://shop.example.com/order/confirmed",
    cancel_url="https://shop.example.com/cart",
    webhook_url="https://shop.example.com/api/webhooks/payment",
    reference="ORD-2024-00542",
    title="Shopping Cart Checkout",
    description="2x Widget Pro, 1x Gadget Mini",
    customer={
        "email": "customer@example.com",
        "name": "Alex Smith",
    },
)

response = client.invoices.create(params)

if response.success:
    print(f"Invoice:       {response.data.invoice_id}")
    print(f"Checkout:      {response.data.checkout_url}")
    print(f"Original:      {response.data.original_amount} {response.data.original_currency}")
    print(f"Stablecoin:    {response.data.amount} {response.data.currency}")
    print(f"Exchange rate: {response.data.exchange_rate}")
```

## Transaction Reporting

Export all transactions for reconciliation:

```python
import csv
from nodela import NodelaClient

client = NodelaClient(api_key="your_api_key")


def export_transactions(output_file="transactions.csv"):
    all_transactions = []
    page = 1

    # Paginate through all transactions
    while True:
        response = client.transactions.list(page=page, limit=50)
        all_transactions.extend(response.data.transactions)

        if not response.data.pagination.has_more:
            break
        page += 1

    # Write to CSV
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Invoice ID", "Reference", "Amount", "Currency",
            "Original Amount", "Original Currency", "Status",
            "Customer Email", "Created At",
        ])

        for txn in all_transactions:
            writer.writerow([
                txn.invoice_id,
                txn.reference,
                txn.amount,
                txn.currency,
                txn.original_amount,
                txn.original_currency,
                txn.status,
                txn.customer.email,
                txn.created_at,
            ])

    print(f"Exported {len(all_transactions)} transactions to {output_file}")


export_transactions()
```

## Error Handling with Retry Logic

Implement custom retry logic on top of the SDK's built-in retries:

```python
import time
from nodela import (
    NodelaClient,
    CreateInvoiceParams,
    RateLimitError,
    ServerError,
    NetworkError,
    NodelaError,
)

client = NodelaClient(api_key="your_api_key")


def create_invoice_with_retry(params, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            return client.invoices.create(params)
        except RateLimitError:
            if attempt < max_attempts:
                wait = 2 ** attempt
                print(f"Rate limited. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
        except (ServerError, NetworkError) as e:
            if attempt < max_attempts:
                wait = 2 ** attempt
                print(f"Transient error: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


params = CreateInvoiceParams(amount=50, currency="USD")
response = create_invoice_with_retry(params)
```

## Using Environment Variables with dotenv

Load your API key from a `.env` file:

```bash
# .env
NODELA_API_KEY=nod_live_your_api_key_here
```

```python
from dotenv import load_dotenv
from nodela import NodelaClient

load_dotenv()

# The SDK automatically reads NODELA_API_KEY
client = NodelaClient()
```
