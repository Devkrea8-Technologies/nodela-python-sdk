"""Models for the Transaction resource."""

from typing import List

from .base import BaseModel


class TransactionCustomer(BaseModel):
    email: str
    name: str


class TransactionPayment(BaseModel):
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


class Transaction(BaseModel):
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


class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_more: bool


class ListTransactionsData(BaseModel):
    transactions: List[Transaction]
    pagination: Pagination


class ListTransactionsResponse(BaseModel):
    success: bool
    data: ListTransactionsData
