from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.db import get_session
from app.models.search_profile import SearchProfile
from app.schemas.search_profile import SearchProfileCreate, SearchProfileRead, SearchProfileUpdate
from app.schemas.search import SearchFilters, SearchResult
from app.services.search_service import run_search

router = APIRouter(prefix="/search-profiles", tags=["search-profiles"])


@router.get("", response_model=list[SearchProfileRead])
async def list_profiles(
    active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
):
    stmt = select(SearchProfile)
    if active is not None:
        stmt = stmt.where(SearchProfile.active == active)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=SearchProfileRead, status_code=201)
async def create_profile(payload: SearchProfileCreate, db: AsyncSession = Depends(get_session)):
    existing = await db.execute(select(SearchProfile).where(SearchProfile.name == payload.name))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Profile with this name already exists")
    now = datetime.utcnow()
    profile = SearchProfile(**payload.model_dump(), created_at=now, updated_at=now)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=SearchProfileRead)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SearchProfile).where(SearchProfile.id == profile_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=SearchProfileRead)
async def update_profile(
    profile_id: int, payload: SearchProfileUpdate, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(SearchProfile).where(SearchProfile.id == profile_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    data = payload.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(profile, k, v)
    profile.updated_at = datetime.utcnow()
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SearchProfile).where(SearchProfile.id == profile_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    await db.delete(profile)
    await db.commit()


@router.post("/{profile_id}/execute", response_model=SearchResult)
async def execute_profile(profile_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SearchProfile).where(SearchProfile.id == profile_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Convert profile to SearchFilters
    all_techs = list(set(profile.skills_required + profile.skills_desired))
    filters = SearchFilters(
        roles=profile.roles,
        role=profile.roles[0] if profile.roles else None,
        levels=profile.levels,
        technologies=all_techs,
        location=profile.location,
        location_mode=profile.location_mode,
        days_ago=profile.days_ago,
        required_words=profile.required_words,
        excluded_words=profile.excluded_words,
        sources=profile.sources,
        max_results=profile.max_results,
        include_unlevel=profile.include_unlevel,
        strategy=profile.strategy,
    )
    return await run_search(filters, db)
