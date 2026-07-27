from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StackCreate(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
    skills: list[int] = []  # list of skill IDs


class StackUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    skills: Optional[list[int]] = None


class StackRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    active: bool
    created_at: datetime
    updated_at: datetime
    skill_ids: list[int] = []

    class Config:
        from_attributes = True
