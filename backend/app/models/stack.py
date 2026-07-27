from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Stack(SQLModel, table=True):
    __tablename__ = "stacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StackSkill(SQLModel, table=True):
    __tablename__ = "stack_skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    stack_id: int = Field(foreign_key="stacks.id", index=True)
    skill_id: int = Field(foreign_key="skills.id", index=True)
    weight: float = 1.0
