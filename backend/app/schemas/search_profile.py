from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SearchProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    roles: list[str] = []
    levels: list[str] = []
    skills_required: list[str] = []
    skills_desired: list[str] = []
    stacks: list[str] = []
    location: Optional[str] = None
    location_mode: str = "brasil"
    days_ago: Optional[int] = None
    required_words: list[str] = []
    excluded_words: list[str] = []
    sources: list[str] = []
    max_results: int = 100
    include_unlevel: bool = False
    strategy: str = "balanced"
    active: bool = True


class SearchProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    roles: Optional[list[str]] = None
    levels: Optional[list[str]] = None
    skills_required: Optional[list[str]] = None
    skills_desired: Optional[list[str]] = None
    stacks: Optional[list[str]] = None
    location: Optional[str] = None
    location_mode: Optional[str] = None
    days_ago: Optional[int] = None
    required_words: Optional[list[str]] = None
    excluded_words: Optional[list[str]] = None
    sources: Optional[list[str]] = None
    max_results: Optional[int] = None
    include_unlevel: Optional[bool] = None
    strategy: Optional[str] = None
    active: Optional[bool] = None


class SearchProfileRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    roles: list[str] = []
    levels: list[str] = []
    skills_required: list[str] = []
    skills_desired: list[str] = []
    stacks: list[str] = []
    location: Optional[str] = None
    location_mode: str = "brasil"
    days_ago: Optional[int] = None
    required_words: list[str] = []
    excluded_words: list[str] = []
    sources: list[str] = []
    max_results: int = 100
    include_unlevel: bool = False
    strategy: str = "balanced"
    active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
