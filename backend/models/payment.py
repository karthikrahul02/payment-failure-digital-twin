from enum import Enum
from pydantic import BaseModel


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class FailureReason(str, Enum):
    TEMPORARY_BANK_ERROR = "TEMPORARY_BANK_ERROR"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    USER_ABANDONMENT = "USER_ABANDONMENT"
    TECHNICAL_ERROR = "TECHNICAL_ERROR"


class CustomerSegment(str, Enum):
    HIGH_RELIABILITY = "HIGH_RELIABILITY"
    MEDIUM_RELIABILITY = "MEDIUM_RELIABILITY"
    LOW_RELIABILITY = "LOW_RELIABILITY"


class Customer(BaseModel):
    customer_id: str
    customer_segment: CustomerSegment
    historical_success_rate: float
    average_transaction_amount: float
    previous_transactions: int
    previous_failures: int


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    payment_method: PaymentMethod
    transaction_hour: int
    status: PaymentStatus
    failure_reason: str | None = None
    retry_count: int