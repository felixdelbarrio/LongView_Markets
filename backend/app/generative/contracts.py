from __future__ import annotations

from pydantic import BaseModel


class GenerativeJobRequest(BaseModel):
    job_type: str = "manual_review"
    entity_type: str = "portfolio"
    entity_id: str = "real"
    prompt_id: str | None = None
