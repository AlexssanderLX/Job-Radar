from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class LinkAccessCreate(BaseModel):
    url: str
    job_id: Optional[int] = None
    search_id: Optional[int] = None
    link_type: str = "job"
    title: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = None
    origin: str = "job_radar"

    @field_validator("url")
    @classmethod
    def valid_http_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("URL must use HTTP or HTTPS")
        return value


class LinkAccessRead(BaseModel):
    id: int
    normalized_url: str
    original_url: str
    job_id: Optional[int]
    search_id: Optional[int]
    link_type: str
    title: Optional[str]
    company: Optional[str]
    source: Optional[str]
    origin: str
    first_accessed_at: datetime
    last_accessed_at: datetime
    access_count: int

    class Config:
        from_attributes = True


class LinkAccessPage(BaseModel):
    items: list[LinkAccessRead]
    total: int
    page: int
    page_size: int
