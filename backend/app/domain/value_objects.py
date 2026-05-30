from __future__ import annotations

from pydantic import BaseModel, Field


class DataLineage(BaseModel):
    source: str
    as_of: str
    confidence: float = Field(ge=0, le=1)
    data_kind: str
    warnings: list[str] = []


class MetricDescription(BaseModel):
    key: str
    label: str
    meaning: str
    calculation: str
    limitations: str
