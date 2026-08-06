from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

from app.utils.url_validator import is_safe_url

ALLOWED_SOURCE_TYPES = {"connector", "manual", "web_search", "rss", "career_page", "api", "github"}


def validate_source_type(value: str) -> str:
    if value not in ALLOWED_SOURCE_TYPES:
        raise ValueError("Unsupported source type")
    return value


def validate_search_template(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    candidate = value.replace("{query}", "backend%20developer")
    if not is_safe_url(candidate):
        raise ValueError("Search URL must be a safe public HTTP(S) URL")
    if "{query}" not in value:
        raise ValueError("Search URL must contain the {query} placeholder")
    return value


class SourceCreate(BaseModel):
    name: str
    display_name: str
    source_type: str = "connector"
    is_manual: bool = False
    active: bool = True
    priority: int = 0
    description: Optional[str] = None
    domain: Optional[str] = None
    search_url_template: Optional[str] = None

    _source_type = field_validator("source_type")(validate_source_type)
    _search_url = field_validator("search_url_template")(validate_search_template)


class SourceUpdate(BaseModel):
    display_name: Optional[str] = None
    source_type: Optional[str] = None
    is_manual: Optional[bool] = None
    active: Optional[bool] = None
    priority: Optional[int] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    search_url_template: Optional[str] = None

    _source_type = field_validator("source_type")(validate_source_type)
    _search_url = field_validator("search_url_template")(validate_search_template)


class SourceRead(BaseModel):
    id: int
    name: str
    display_name: str
    source_type: str
    is_manual: bool
    active: bool
    priority: int
    description: Optional[str] = None
    domain: Optional[str] = None
    search_url_template: Optional[str] = None
    last_run: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
