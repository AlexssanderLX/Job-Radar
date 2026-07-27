from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    aliases: list[str] = []
    excluded_words: list[str] = []
    active: bool = True


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    aliases: Optional[list[str]] = None
    excluded_words: Optional[list[str]] = None
    active: Optional[bool] = None


class RoleRead(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    aliases: list[str] = []
    excluded_words: list[str] = []
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
