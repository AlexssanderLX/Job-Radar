from datetime import datetime
from typing import Optional
from pydantic import BaseModel, computed_field, field_validator


class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    modality: Optional[str] = None
    level: Optional[str] = None
    description: Optional[str] = None
    technologies: list[str] = []
    source: str
    url: str
    apply_url: str
    published_at: Optional[datetime] = None
    collected_at: datetime
    match_score: float = 0.0
    match_reasons: list[str] = []
    match_penalties: list[str] = []
    match_summary: Optional[str] = None
    is_manual: bool = False
    external_id: Optional[str] = None
    summary: Optional[str] = None
    source_type: str = "connector"
    result_type: str = "job"
    query_origin: Optional[str] = None
    raw_title: Optional[str] = None
    raw_snippet: Optional[str] = None
    related_sources: list[str] = []

    @field_validator("url", "apply_url", mode="before")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v:
            return v
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"URL must start with http:// or https://: {v}")
        return v


class JobCreate(JobBase):
    pass


class JobRead(JobBase):
    id: int
    first_seen_at: datetime
    last_seen_at: datetime
    is_favorite: bool = False
    is_hidden: bool = False
    applied: bool = False
    notes: Optional[str] = None
    status: str = "new"
    applied_at: Optional[datetime] = None
    tags: list[str] = []
    first_accessed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    access_count: int = 0

    @computed_field
    @property
    def has_been_accessed(self) -> bool:
        return self.access_count > 0

    class Config:
        from_attributes = True


class JobUpdate(BaseModel):
    is_favorite: Optional[bool] = None
    is_hidden: Optional[bool] = None
    applied: Optional[bool] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    applied_at: Optional[datetime] = None
    tags: Optional[list[str]] = None
