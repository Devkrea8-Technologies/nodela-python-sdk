# Transactions

The Transactions resource lets you retrieve a paginated list of your completed transactions.

## List Transactions

```python
client.transactions.list(
    page: int | None = None,
    limit: int | None = None,
) -> ListTransactionsResponse
```

Returns a paginated list of transactions associated with your account.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | `int` | No | API default | Page number (starts at 1). |
| `limit` | `int` | No | API default | Number of results per page. |

### Example

```python
from nodela import NodelaClient

client = NodelaClient(api_key="your_api_key")

# Fetch the first page of transactions
response = client.transactions.list(page=1, limit=10)

for txn in response.data.transactions:
    print(
        f"{txn.invoice_id} | "
        f"{txn.original_amount} {txn.original_currency} | "
        f"{txn.status}"
    )

# Pagination info
pagination = response.data.pagination
print(f"Page {pagination.page} of {pagination.total_pages}")
print(f"Total transactions: {pagination.total}")

if pagination.has_more:
    # Fetch the next page
    next_page = client.transactions.list(page=pagination.page + 1, limit=10)
```

### Iterating Through All Pages

```python
page = 1
all_transactions = []

while True:
    response = client.transactions.list(page=page, limit=50)
    all_transactions.extend(response.data.transactions)

    if not response.data.pagination.has_more:
        break
    page += 1

print(f"Total fetched: {len(all_transactions)}")
```

### Response

`ListTransactionsResponse` fields:

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the request succeeded. |
| `data` | `ListTransactionsData` | Transaction list and pagination. |

`ListTransactionsData` fields:

| Field | Type | Description |
|-------|------|-------------|
| `transactions` | `List[Transaction]` | List of transaction records. |
| `pagination` | `Pagination` | Pagination metadata. |

### Transaction Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Internal record ID. |
| `invoice_id` | `str` | Associated invoice ID. |
| `reference` | `str` | Your internal reference. |
| `original_amount` | `float` | Amount in original fiat currency. |
| `original_currency` | `str` | Original fiat currency code. |
| `amount` | `float` | Stablecoin amount. |
| `currency` | `str` | Stablecoin currency code. |
| `exchange_rate` | `float` | Conversion rate used. |
| `title` | `str` | Invoice title. |
| `description` | `str` | Invoice description. |
| `status` | `str` | Transaction status. |
| `paid` | `bool` | Whether the payment was confirmed. |
| `customer` | `TransactionCustomer` | Customer details (`email`, `name`). |
| `created_at` | `str` | ISO 8601 creation timestamp. |
| `payment` | `TransactionPayment` | Payment details (network, token, tx_hash, etc.). |

### Pagination Object

| Field | Type | Description |
|-------|------|-------------|
| `page` | `int` | Current page number. |
| `limit` | `int` | Results per page. |
| `total` | `int` | Total number of transactions. |
| `total_pages` | `int` | Total number of pages. |
| `has_more` | `bool` | Whether more pages are available. |
