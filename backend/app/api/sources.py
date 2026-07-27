from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.db import get_session
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceRead])
async def list_sources(
    active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
):
    stmt = select(Source)
    if active is not None:
        stmt = stmt.where(Source.active == active)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=SourceRead, status_code=201)
async def create_source(payload: SourceCreate, db: AsyncSession = Depends(get_session)):
    existing = await db.execute(select(Source).where(Source.name == payload.name))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Source with this name already exists")
    now = datetime.utcnow()
    source = Source(**payload.model_dump(), created_at=now, updated_at=now)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.patch("/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: int, payload: SourceUpdate, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalars().first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    data = payload.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(source, k, v)
    source.updated_at = datetime.utcnow()
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalars().first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    await db.delete(source)
    await db.commit()
