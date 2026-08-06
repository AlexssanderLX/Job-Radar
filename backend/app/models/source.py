from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    display_name: str
    source_type: str = "connector"  # connector, manual, google, github
    is_manual: bool = False
    active: bool = True
    priority: int = 0
    description: Optional[str] = None
    domain: Optional[str] = None
    search_url_template: Optional[str] = None
    last_run: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
