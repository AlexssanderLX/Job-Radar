from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SourceCreate(BaseModel):
    name: str
    display_name: str
    source_type: str = "connector"
    is_manual: bool = False
    active: bool = True
    priority: int = 0
    description: Optional[str] = None


class SourceUpdate(BaseModel):
    display_name: Optional[str] = None
    source_type: Optional[str] = None
    is_manual: Optional[bool] = None
    active: Optional[bool] = None
    priority: Optional[int] = None
    description: Optional[str] = None


class SourceRead(BaseModel):
    id: int
    name: str
    display_name: str
    source_type: str
    is_manual: bool
    active: bool
    priority: int
    description: Optional[str] = None
    last_run: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
