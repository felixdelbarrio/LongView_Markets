from __future__ import annotations

from enum import StrEnum


class DataKind(StrEnum):
    OBSERVED = "observed"
    MOCK = "mock"
    SIMULATION = "simulation"
    FORECAST = "forecast"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransactionType(StrEnum):
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
