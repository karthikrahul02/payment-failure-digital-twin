from typing import Optional, Literal
from pydantic import BaseModel, Field


class FailedPaymentRequest(BaseModel):
    transaction_id: str = Field(
        ...,
        json_schema_extra={"example": "TXN_API_001"}
    )

    customer_id: str = Field(
        ...,
        json_schema_extra={"example": "CUST_API_001"}
    )

    amount: float = Field(
        ...,
        gt=0,
        json_schema_extra={"example": 5000.0}
    )

    payment_method: Literal[
        "CARD",
        "UPI",
        "WALLET",
        "NET_BANKING"
    ] = Field(
        ...,
        json_schema_extra={"example": "UPI"}
    )

    failure_reason: Literal[
        "TEMPORARY_BANK_ERROR",
        "INSUFFICIENT_FUNDS",
        "TECHNICAL_ERROR",
        "NETWORK_TIMEOUT",
        "USER_ABANDONMENT",
        "AUTHENTICATION_FAILURE"
    ] = Field(
        ...,
        json_schema_extra={"example": "TEMPORARY_BANK_ERROR"}
    )

    customer_segment: Literal[
        "MEDIUM_RELIABILITY",
        "HIGH_RELIABILITY",
        "LOW_RELIABILITY"
    ] = Field(
        default="MEDIUM_RELIABILITY",
        json_schema_extra={"example": "MEDIUM_RELIABILITY"}
    )

    historical_success_rate: float = Field(
        default=0.85,
        ge=0,
        le=1,
        json_schema_extra={"example": 0.85}
    )

    average_transaction_amount: Optional[float] = Field(
        default=None,
        gt=0,
        json_schema_extra={"example": 4500.0}
    )

    transaction_hour: int = Field(
        default=14,
        ge=0,
        le=23,
        json_schema_extra={"example": 14}
    )

    customer_success_category: Literal[
        "MEDIUM",
        "HIGH",
        "LOW"
    ] = Field(
        default="MEDIUM",
        json_schema_extra={"example": "MEDIUM"}
    )