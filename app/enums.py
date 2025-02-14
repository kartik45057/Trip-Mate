from pydantic import BaseModel
from enum import Enum

class PaymentMode(str, Enum):
    CASH = "Cash",
    CREDIT_CARD = "Credit Card",
    DEBIT_CARD = "Debit Card",
    BANK_TRANSFER = "Bank Transfer",
    CHECK = "Check",
    DIGITAL_WALLET = "Digital Wallet",
    UPI = "UPI",
    BNPL = "Buy Now, Pay Later"

class CurrencyCode(str, Enum):
    INR = "INR",
    USD = "USD",
    EUR = "EUR"