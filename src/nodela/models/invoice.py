"""Models for the Invoice resource."""

from typing import List, Literal, Optional

from .base import BaseModel

SUPPORTED_CURRENCIES = [
    # Americas
    "USD",
    "CAD",
    "MXN",
    "BRL",
    "ARS",
    "CLP",
    "COP",
    "PEN",
    "JMD",
    "TTD",
    # Europe
    "EUR",
    "GBP",
    "CHF",
    "SEK",
    "NOK",
    "DKK",
    "PLN",
    "CZK",
    "HUF",
    "RON",
    "BGN",
    "HRK",
    "ISK",
    "TRY",
    "RUB",
    "UAH",
    # Africa
    "NGN",
    "ZAR",
    "KES",
    "GHS",
    "EGP",
    "MAD",
    "TZS",
    "UGX",
    "XOF",
    "XAF",
    "ETB",
    # Asia
    "JPY",
    "CNY",
    "INR",
    "KRW",
    "IDR",
    "MYR",
    "THB",
    "PHP",
    "VND",
    "SGD",
    "HKD",
    "TWD",
    "BDT",
    "PKR",
    "LKR",
    # Middle East
    "AED",
    "SAR",
    "QAR",
    "KWD",
    "BHD",
    "OMR",
    "ILS",
    "JOD",
    # Oceania
    "AUD",
    "NZD",
    "FJD",
]

SupportedCurrency = Literal[
    # Americas
    "USD",
    "CAD",
    "MXN",
    "BRL",
    "ARS",
    "CLP",
    "COP",
    "PEN",
    "JMD",
    "TTD",
    # Europe
    "EUR",
    "GBP",
    "CHF",
    "SEK",
    "NOK",
    "DKK",
    "PLN",
    "CZK",
    "HUF",
    "RON",
    "BGN",
    "HRK",
    "ISK",
    "TRY",
    "RUB",
    "UAH",
    # Africa
    "NGN",
    "ZAR",
    "KES",
    "GHS",
    "EGP",
    "MAD",
    "TZS",
    "UGX",
    "XOF",
    "XAF",
    "ETB",
    # Asia
    "JPY",
    "CNY",
    "INR",
    "KRW",
    "IDR",
    "MYR",
    "THB",
    "PHP",
    "VND",
    "SGD",
    "HKD",
    "TWD",
    "BDT",
    "PKR",
    "LKR",
    # Middle East
    "AED",
    "SAR",
    "QAR",
    "KWD",
    "BHD",
    "OMR",
    "ILS",
    "JOD",
    # Oceania
    "AUD",
    "NZD",
    "FJD",
]


# --- Request models ---


class CustomerParams(BaseModel):
    email: str
    name: Optional[str] = None


class CreateInvoiceParams(BaseModel):
    amount: float
    currency: SupportedCurrency
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    webhook_url: Optional[str] = None
    reference: Optional[str] = None
    customer: Optional[CustomerParams] = None
    title: Optional[str] = None
    description: Optional[str] = None


# --- Response models ---


class ErrorDetail(BaseModel):
    code: str
    message: str


class CustomerInfo(BaseModel):
    email: str
    name: Optional[str] = None


class CreateInvoiceData(BaseModel):
    id: str
    invoice_id: str
    original_amount: str
    original_currency: str
    amount: str
    currency: str
    exchange_rate: Optional[str] = None
    webhook_url: Optional[str] = None
    customer: Optional[CustomerInfo] = None
    checkout_url: str
    status: Optional[str] = None
    created_at: str


class CreateInvoiceResponse(BaseModel):
    success: bool
    error: Optional[ErrorDetail] = None
    data: Optional[CreateInvoiceData] = None


class PaymentInfo(BaseModel):
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


class VerifyInvoiceData(BaseModel):
    id: str
    invoice_id: str
    reference: Optional[str] = None
    original_amount: str
    original_currency: str
    amount: float
    currency: str
    exchange_rate: Optional[float] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: str
    paid: bool
    customer: Optional[CustomerInfo] = None
    created_at: str
    payment: Optional[PaymentInfo] = None


class VerifyInvoiceResponse(BaseModel):
    success: bool
    data: Optional[VerifyInvoiceData] = None
    error: Optional[ErrorDetail] = None
