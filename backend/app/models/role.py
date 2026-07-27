from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    category: Optional[str] = None
    description: Optional[str] = None
    aliases: list[str] = Field(default=[], sa_column=Column(JSON))
    excluded_words: list[str] = Field(default=[], sa_column=Column(JSON))
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
