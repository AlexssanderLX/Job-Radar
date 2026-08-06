from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def run_migrations() -> None:
    """Add new columns to existing tables safely (SQLite ALTER TABLE)."""
    migrations = [
        "ALTER TABLE jobs ADD COLUMN status TEXT DEFAULT 'new'",
        "ALTER TABLE jobs ADD COLUMN applied_at TEXT",
        "ALTER TABLE jobs ADD COLUMN tags TEXT DEFAULT '[]'",
        "ALTER TABLE jobs ADD COLUMN summary TEXT",
        "ALTER TABLE jobs ADD COLUMN source_type TEXT DEFAULT 'connector'",
        "ALTER TABLE jobs ADD COLUMN result_type TEXT DEFAULT 'job'",
        "ALTER TABLE jobs ADD COLUMN query_origin TEXT",
        "ALTER TABLE jobs ADD COLUMN raw_title TEXT",
        "ALTER TABLE jobs ADD COLUMN raw_snippet TEXT",
        "ALTER TABLE jobs ADD COLUMN related_sources TEXT DEFAULT '[]'",
        "ALTER TABLE jobs ADD COLUMN first_accessed_at TEXT",
        "ALTER TABLE jobs ADD COLUMN last_accessed_at TEXT",
        "ALTER TABLE jobs ADD COLUMN access_count INTEGER DEFAULT 0",
        "ALTER TABLE sources ADD COLUMN domain TEXT",
        "ALTER TABLE sources ADD COLUMN search_url_template TEXT",
    ]
    async with engine.begin() as conn:
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception:
                # Column already exists — safe to ignore
                pass


async def init_db() -> None:
    # Import all models so SQLModel knows about them
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Add new columns to existing tables
    await run_migrations()


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
