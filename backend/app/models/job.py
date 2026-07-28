from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    company: str
    location: Optional[str] = None
    modality: Optional[str] = None
    level: Optional[str] = None
    description: Optional[str] = None
    technologies: list[str] = Field(default=[], sa_column=Column(JSON))
    source: str
    url: str = Field(index=True)
    apply_url: str
    published_at: Optional[datetime] = None
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    match_score: float = 0.0
    match_reasons: list[str] = Field(default=[], sa_column=Column(JSON))
    match_penalties: list[str] = Field(default=[], sa_column=Column(JSON))
    match_summary: Optional[str] = None
    is_manual: bool = False
    external_id: Optional[str] = None
    summary: Optional[str] = None
    source_type: str = "connector"
    result_type: str = "job"
    query_origin: Optional[str] = None
    raw_title: Optional[str] = None
    raw_snippet: Optional[str] = None
    related_sources: list[str] = Field(default=[], sa_column=Column(JSON))

    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    is_favorite: bool = False
    is_hidden: bool = False
    applied: bool = False
    notes: Optional[str] = None

    # New fields
    status: str = Field(default="new")  # new, evaluating, favorite, applied, interview, rejected, archived
    applied_at: Optional[datetime] = None
    tags: list[str] = Field(default=[], sa_column=Column(JSON))


class SearchHistory(SQLModel, table=True):
    __tablename__ = "search_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    filters: dict = Field(default={}, sa_column=Column(JSON))
    searched_at: datetime = Field(default_factory=datetime.utcnow)
    total_found: int = 0
    sources_searched: list[str] = Field(default=[], sa_column=Column(JSON))
    sources_failed: list[str] = Field(default=[], sa_column=Column(JSON))
    duration_seconds: float = 0.0


class SavedFilter(SQLModel, table=True):
    __tablename__ = "saved_filters"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    filters: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
