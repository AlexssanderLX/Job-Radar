from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON


class SearchProfile(SQLModel, table=True):
    __tablename__ = "search_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    roles: list[str] = Field(default=[], sa_column=Column(JSON))
    levels: list[str] = Field(default=[], sa_column=Column(JSON))
    skills_required: list[str] = Field(default=[], sa_column=Column(JSON))
    skills_desired: list[str] = Field(default=[], sa_column=Column(JSON))
    stacks: list[str] = Field(default=[], sa_column=Column(JSON))

    location: Optional[str] = None
    location_mode: str = "brasil"
    days_ago: Optional[int] = None
    required_words: list[str] = Field(default=[], sa_column=Column(JSON))
    excluded_words: list[str] = Field(default=[], sa_column=Column(JSON))
    sources: list[str] = Field(default=[], sa_column=Column(JSON))
    max_results: int = 100
    include_unlevel: bool = False
    strategy: str = "balanced"

    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
